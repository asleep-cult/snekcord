from __future__ import annotations

import asyncio
import enum
import platform
import random
import time

from loguru import logger

from wsaio import (
    HandshakeFailureError,
    WebSocketClient,
    WebSocketCloseCode,
)

from ..exceptions import (
    AuthenticationFailedError,
    DisallowedIntentsError,
    PendingCancellationError,
    ShardCloseError,
)
from ..json import dump_json, load_json
from ..undefined import undefined

__all__ = (
    'ShardOpcode',
    'ShardCloseCode',
    'Shard',
    'ShardWebSocket',
)


class ShardOpcode(enum.IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class ShardCloseCode(enum.IntEnum):
    UNKNOWN_ERROR = 4000
    UNKNOWN_OPCODE = 4001
    DECODE_ERROR = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    INVALID_SEQUENCE = 4007
    RATELIMITED = 4008
    SESSION_TIMED_OUT = 4009
    INVALID_SHARD = 4010
    SHARDING_REQUIRED = 4011
    INVALID_API_VERSION = 4012
    INVALID_INTENTS = 4013
    DISALLOWED_INTENTS = 4014


class ShardGuildStatus(enum.IntEnum):
    UNKNOWN = enum.auto()
    UNAVAILABLE = enum.auto()
    AVAILABLE = enum.auto()


class ShardCancellationToken(enum.IntEnum):
    HANDSHAKE_FAILED = enum.auto()
    HELLO_TIMEOUT = enum.auto()
    READY_TIMEOUT = enum.auto()

    INVALID_HEARTBEAT_INTERVAL = enum.auto()
    INVALID_HELLO_DATA = enum.auto()

    RECONNECT_RECEIVED = enum.auto()
    BINARY_RECEIVED = enum.auto()
    INVALID_SESSION = enum.auto()
    SIGNAL_INTERRUPT = enum.auto()

    CONNECTION_CLOSED = enum.auto()


def set_result(future, result) -> None:
    try:
        future.set_result(result)
    except asyncio.InvalidStateError:
        return None


def set_exception(future, exception) -> None:
    try:
        future.set_exception(exception)
    except asyncio.InvalidStateError:
        return None


class ShardWebSocket(WebSocketClient):
    def __init__(self, shard: Shard) -> None:
        super().__init__(loop=shard.loop)
        self.shard = shard
        self.detached = False

    async def send_json(self, data):
        await self.send(dump_json(data))

    async def send_heartbeat(self):
        logger.info('WebSocket sending HEARTBEAT payload')
        await self.send_json({'op': ShardOpcode.HEARTBEAT, 'd': None})

    async def send_identify(self, token, properties, intents, *, shard=None, large_threshold=None):
        payload = {
            'op': ShardOpcode.IDENTIFY,
            'd': {
                'token': token,
                'properties': properties,
                'intents': int(intents),
            },
        }

        if shard is not None:
            payload['d']['shard'] = shard

        if large_threshold is not None:
            large_threshold = int(large_threshold)

            if not 50 >= large_threshold <= 250:
                raise ValueError('large_threshold should be >= 50 and <= 250')

            payload['d']['large_threshold'] = large_threshold

        logger.info('WebSocket sending IDENTIFY payload')
        await self.send_json(payload)

    async def send_resume(self, token, session_id, sequence):
        payload = {
            'op': ShardOpcode.RESUME,
            'd': {
                'tokens': token,
                'session_id': session_id,
                'seq': sequence,
            },
        }

        logger.info('WebSocket sending resume payload')
        await self.send_json(payload)

    async def request_guild_members(
        self, guild, *, query=None, limit=None, presences=None, users=undefined, nonce=None
    ):
        data = JSONBuilder()

        guild_id = self.shard.client.guilds.to_unique(guild)
        data.snowflake(guild_id)

        if query is not None:
            if users is not None:
                raise TypeError('query and users are mutually exclusive')

            data.str('query', query)

            if limit is not None:
                data.int('limit', limit)
            else:
                data.int('limit', 0)
        else:
            if users is None:
                raise TypeError('one of (query, users) must be provided')

            user_ids = set()
            for user in users:
                user_ids.add(self.shard.client.users.to_unique(user))

            data.snowflake_array('users', user_ids)

            if limit is not None:
                data.int('limit', limit)

        data.bool('presences', presences)

        if nonce is not None:
            nonce = str(nonce)
            if len(nonce.encode('utf-8')) > 32:
                raise TypeError('nonce must be <= 32 bytes')

            data.str('nonce', nonce)

        logger.info(f'WebSocket requesting guild members in {guild_id}')
        await self.send_json({'op': ShardOpcode.REQUEST_GUILD_MEMBERS, 'd': data})

    async def update_voice_state(self, guild, channel, *, mute=False, deaf=False):
        data = JSONBuilder()

        data.snowflake('guild_id', self.shard.client.guilds.to_unique(guild))

        if channel is not None:
            channel = self.shard.client.channels.to_unique(channel)

        channel_id = self.shard.client.channeld.to_unique(channel)
        data.snowflake('channel_id', channel_id, nullable=True)

        data.bool('self_mute', mute)
        data.bool('self_deaf', deaf)

        logger.info(f'WebSocket updating voice state in {channel_id}')
        await self.send_json({'op': ShardOpcode.VOICE_STATE_UPDATE, 'd': data})

    async def on_text(self, data: str) -> None:
        if self.detached:
            return logger.debug('WebSocket received text but it is detached')

        try:
            payload = load_json(data)
        except Exception:
            return logger.debug('WebSocket received non-JSON text payload')

        if not isinstance(payload, dict):
            return logger.debug('WebSocket received non-object JSON payload')

        try:
            opcode = ShardOpcode(payload['op'])
        except (KeyError, ValueError):
            return logger.debug('WebSocket received payload with invalid opcode')

        logger.info(f'WebSocket received {opcode.name} payload')

        if opcode is ShardOpcode.DISPATCH:
            event = payload.get('t')
            if not isinstance(event, str):
                return logger.debug('WebSocket received DISPATCH payload with invalid event name')

            sequence = payload.get('s')
            if not isinstance(sequence, int):
                return logger.debug('WebSocket received DISPATCH payload with invalid sequence')

            data = payload.get('d')
            if not isinstance(data, dict):
                return logger.debug('WebSocket received DISPATCH payload with invalid data')

            await self.shard.on_dispatch(event, sequence, data)

        elif opcode is ShardOpcode.HEARTBEAT:
            await self.send_heartbeat()

        elif opcode is ShardOpcode.INVALID_SESSION:
            reconnect = payload.get('d')
            if not isinstance(reconnect, bool):
                reconnect = False
                logger.debug(
                    'WebSocket received INVALID_SESSION payload with invalid reconnect flag'
                )

            await self.shard.on_invalid_session(reconnect)

        elif opcode is ShardOpcode.HELLO:
            data = payload.get('d')
            if not isinstance(data, dict):
                await self.shard.cancel(ShardCancellationToken.INVALID_HELLO_DATA)
            else:
                await self.shard.on_hello(data)

        elif opcode is ShardOpcode.HEARTBEAT_ACK:
            await self.shard.on_heartbeat_ack()

    async def on_binary(self, data):
        if self.detached:
            return logger.debug('WebSocket received binary but it is detached')

        await self.shard.cancel(ShardCancellationToken.BINARY_RECEIVED)

    async def on_close(self, data, code):
        if self.detached:
            return logger.debug('WebSocket received close but it is detached')

        await self.shard.cancel(ShardCancellationToken.CONNECTION_CLOSED, (data, code))

    def detach(self):
        self.detached = True


class ShardBeater:
    def __init__(self, shard):
        self.shard = shard
        self.interval = None

        self.sendtime = float('nan')
        self.acktime = float('nan')
        self.latency = float('nan')

        self.stopping = False

    def create_task(self):
        return self.shard.loop.create_task(self.beat())

    def calculate_jitter(self):
        return random.random() * self.interval

    async def beat(self):
        if not self.stopping and self.shard.ws is not None:
            await self.shard.ws.send_heartbeat()
            self.sendtime = time.monotonic()

            self.shard.loop.call_later(self.interval, self.create_task)

    def ack(self):
        self.acktime = time.monotonic()
        self.latency = self.acktime - self.sendtime

    def start(self, interval):
        self.interval = interval
        self.shard.loop.call_later(self.calculate_jitter(), self.create_task)

    def stop(self):
        self.stopping = True


class Shard:
    def __init__(self, client, url, shard_id, *, sharded=False):
        self.client = client
        self.url = url
        self.shard_id = shard_id
        self.sharded = sharded

        self.token = self.client.authorization.token
        self.intents = self.client.intents
        self.loop = self.client.loop

        self.ws = None
        self.beater = None

        self._attempts = 0
        self._cancellation_queue = asyncio.Queue()

        self._sequence = -1
        self._session_id = None
        self._guilds = {}
        self._hello_fut = None
        self._ready_fut = None

        self._task = None

    @property
    def latency(self):
        if self.beater is None:
            return float('nan')
        else:
            return self.beater.latency

    def create_websocket(self):
        self.ws = ShardWebSocket(self)

    def create_beater(self):
        self.beater = ShardBeater(self)

    async def wait_for_hello(self):
        await asyncio.wait_for(self._hello_fut, timeout=30)

    async def wait_for_ready(self):
        await asyncio.wait_for(self._ready_fut, timeout=30)

    def get_identify_properties(self):
        return {'$os': platform.system(), '$browser': 'snekcord', '$device': 'snekcord'}

    async def create_connection(self, *, reconnect=False):
        self._attempts += 1

        self.create_websocket()
        self.create_beater()

        self._hello_fut = self.loop.create_future()
        self._ready_fut = self.loop.create_future()

        try:
            await self.ws.connect(self.url)
        except HandshakeFailureError:
            return await self.cancel(ShardCancellationToken.HANDSHAKE_FAILED)

        try:
            await self.wait_for_hello()
        except asyncio.TimeoutError:
            return await self.cancel(ShardCancellationToken.HELLO_TIMEOUT)

        if reconnect and self._session_id is not None:
            await self.ws.send_resume(self.token, self._session_id, self._sequence)
        else:
            if self.sharded:
                shard = (self.shard_id, len(self.client.shard_ids))
            else:
                shard = None

            await self.ws.send_identify(
                self.token, self.get_identify_properties(), self.intents, shard=shard
            )

        try:
            await self.wait_for_ready()
        except asyncio.TimeoutError:
            return await self.cancel(ShardCancellationToken.READY_TIMEOUT)

    async def on_hello(self, data):
        assert self._hello_fut is not None
        set_result(self._hello_fut, None)

        interval = data.get('heartbeat_interval')
        if not isinstance(interval, int):
            await self.cancel(ShardCancellationToken.INVALID_HEARTBEAT_INTERVAL)
        else:
            assert self.beater is not None
            self.beater.start(interval / 1000)

    async def on_heartbeat_ack(self):
        assert self.beater is not None
        self.beater.ack()

    async def on_dispatch(self, event, sequence, data):
        if sequence > self._sequence:
            self._sequence = sequence

        if event == 'READY':
            session_id = data.get('session_id')
            if not isinstance(session_id, str):
                logger.debug('WebSocket received READY payload with invalid session_id')
            else:
                self._session_id = session_id

            user = data.get('user')
            if not isinstance(user, dict):
                logger.debug('WebSocket received HELLO payload with invalid user')
            else:
                await self.client.users.upsert(user)

            guilds = data.get('guilds')
            if not isinstance(guilds, list):
                logger.debug('WebSocket received HELLO payload with invalid guilds')
            else:
                for guild in guilds:
                    self._guilds[guild['id']] = ShardGuildStatus.UNKNOWN

            assert self._ready_fut is not None
            return set_result(self._ready_fut, None)

        if event == 'RESUMED':
            assert self._ready_fut is not None
            return set_result(self._ready_fut, None)

        if event == 'GUILD_CREATE':
            guild_id = data['id']

            state = self._guilds.get(guild_id)
            if state is None:
                event = 'GUILD_JOIN'
            elif state is ShardGuildStatus.UNAVAILABLE:
                event = 'GUILD_AVAILABLE'
            else:
                event = 'GUILD_RECEIVE'

            self._guilds[guild_id] = ShardGuildStatus.AVAILABLE

        elif event == 'GUILD_DELETE':
            guild_id = data['id']

            if data.get('unavailable', False):
                event = 'GUILD_UNAVAILABLE'
                self._guilds[guild_id] = ShardGuildStatus.UNAVAILABLE
            else:
                self._guilds.pop(guild_id, None)

        state = self.client.get_event(event)
        if state is not None:
            await state.dispatch(event, self, data)
        else:
            logger.debug(f'WebSocket received unhandled event {event!r}')

    async def on_reconnect(self):
        await self.cancel(ShardCancellationToken.RECONNECT_RECEIVED)

    async def on_invalid_session(self, reconnect):
        await self.cancel(ShardCancellationToken.INVALID_SESSION, reconnect)

    async def cancel(self, token, info=None):
        await self._cancellation_queue.put((token, info))

        if self._hello_fut is not None:
            set_exception(self._hello_fut, PendingCancellationError)

        if self._ready_fut is not None:
            set_exception(self._ready_fut, PendingCancellationError)

    def start(self) -> None:
        self._task = self.loop.create_task(self.run())

    async def join(self) -> None:
        await self._task

    async def run(self):
        stopping = False
        reconnect = False

        while not stopping:
            self._connected_at = time.monotonic()

            try:
                await self.create_connection(reconnect=reconnect)
            except PendingCancellationError:
                assert not self._cancellation_queue.empty()

            if self._cancellation_queue.empty():
                latency = time.monotonic() - self._connected_at
                logger.info(f'Shard established WebSocket connection after {latency * 1000:.3f}ms')

            reconnect = False
            token, info = await self._cancellation_queue.get()

            if self.beater is not None:
                self.beater.stop()

            if token is ShardCancellationToken.HANDSHAKE_FAILED:
                logger.warning('Shard closing due to handshake failure')

            elif token is ShardCancellationToken.HELLO_TIMEOUT:
                logger.warning('Shard closing because HELLO was not sent in time')
                await self.ws.close(code=WebSocketCloseCode.POLICY_VIOLATION)

            elif token is ShardCancellationToken.READY_TIMEOUT:
                logger.warning('Shard closing because READY was not sent in time')
                await self.ws.close(code=WebSocketCloseCode.POLICY_VIOLATION)

            if token is ShardCancellationToken.INVALID_HEARTBEAT_INTERVAL:
                logger.warning('Shard closing due to invalid hearbeat interval')
                await self.ws.close(code=WebSocketCloseCode.POLICY_VIOLATION)

            elif token is ShardCancellationToken.INVALID_HELLO_DATA:
                logger.warning('Shard closing due to invalid HELLO data')
                await self.ws.close(code=WebSocketCloseCode.POLICY_VIOLATION)

            elif token is ShardCancellationToken.RECONNECT_RECEIVED:
                reconnect = True

                logger.debug('Shard closing because a RECONNECT was issued')
                await self.ws.close(code=WebSocketCloseCode.NORMAL_CLOSURE)

            elif token is ShardCancellationToken.BINARY_RECEIVED:
                logger.warning('Shard closing due to binary data')
                await self.ws.close(code=WebSocketCloseCode.UNSUPPORTED_DATA)

            elif token is ShardCancellationToken.INVALID_SESSION:
                reconnect = info

                logger.debug('Shard closing bacause an INVALID_SESSION was issued')
                await self.ws.close(code=WebSocketCloseCode.NORMAL_CLOSURE)

                await asyncio.sleep(1 + random.random() * 5)

            elif token is ShardCancellationToken.SIGNAL_INTERRUPT:
                stopping = True

                logger.debug('Shard closing due to a signal interrupt')
                await self.ws.close(code=WebSocketCloseCode.NORMAL_CLOSURE)

            elif token is ShardCancellationToken.CONNECTION_CLOSED:
                if info[1] == ShardCloseCode.AUTHENTICATION_FAILED:
                    raise AuthenticationFailedError(self)

                if info[1] == ShardCloseCode.DISALLOWED_INTENTS:
                    raise DisallowedIntentsError(self)

                if info[1] in (
                    ShardCloseCode.INVALID_SHARD,
                    ShardCloseCode.SHARDING_REQUIRED,
                    ShardCloseCode.INVALID_API_VERSION,
                    ShardCloseCode.INVALID_INTENTS,
                ):
                    raise ShardCloseError(ShardCloseCode(info[1]), self)

                logger.debug(f'Shard closed [{info[1]}]: {info[0].decode()}')

            if self.ws.is_closing() and token is not ShardCancellationToken.CONNECTION_CLOSED:
                try:
                    token, _ = await asyncio.wait_for(self._cancellation_queue.get(), timeout=10)
                except asyncio.TimeoutError:
                    token = None

                if token is ShardCancellationToken.SIGNAL_INTERRUPT:
                    logger.debug(
                        'Shard interrupted while waiting for '
                        'CONNECTION_CLOSED, detaching WebSocket'
                    )
                    stopping = True
                    self.ws.detach()

                elif token is not ShardCancellationToken.CONNECTION_CLOSED:
                    name = token.name if token is not None else None
                    logger.warning(
                        f'Shard expected CONNECTION_CLOSED token but found '
                        f'{name} instead, detaching WebSocket'
                    )
                    self.ws.detach()

            try:
                await self.ws.stream.close()
            except Exception:
                logger.exception('Shard failed to close WebSocket due to an exception, ignoring')

            if not stopping and time.monotonic() - self._connected_at < 5:
                await asyncio.sleep(1 + random.random() * self._attempts)
            else:
                self._attempts = 0

            while not self._cancellation_queue.empty():
                token, _ = self._cancellation_queue.get_nowait()
                logger.debug(
                    f'Shard found unhandled token {token.name} in cancellation queue, discarding'
                )

                if token is ShardCancellationToken.SIGNAL_INTERRUPT:
                    stopping = True

        await self.cleanup()

    async def cleanup(self) -> None:
        if self._hello_fut is not None:
            self._ready_fut.cancel()

        if self._ready_fut is not None:
            self._ready_fut.cancel()
