from __future__ import annotations

import asyncio
import contextlib
import enum
import platform
import random
import time
import typing

import wsaio
from loguru import logger

from ..exceptions import (
    AuthenticationFailedError,
    DisallowedIntentsError,
    PendingCancellationError,
    ShardCloseError,
)
from ..json import JSONObject, dump_json, json_get, load_json

if typing.TYPE_CHECKING:
    from ..clients import WebSocketClient
    from ..states import SupportsChannelID, SupportsGuildID, SupportsUserID

__all__ = (
    'ShardOpcode',
    'ShardCloseCode',
    'Shard',
    'ShardWebSocket',
)

T = typing.TypeVar('T')


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

    CONNECTION_CLOSING = enum.auto()
    CONNECTION_CLOSED = enum.auto()


class ShardWebSocket(wsaio.WebSocketClient):
    def __init__(self, shard: Shard) -> None:
        super().__init__(loop=shard.loop)
        self.shard = shard
        self.detached = False

    async def send_json(self, data: JSONObject) -> None:
        await self.send(dump_json(data))

    async def send_heartbeat(self) -> None:
        logger.info('WebSocket sending HEARTBEAT payload')
        await self.send_json({'op': ShardOpcode.HEARTBEAT, 'd': None})

    async def send_identify(
        self,
        token: str,
        properties: JSONObject,
        intents: int,
        *,
        shard: typing.Optional[typing.Tuple[int, int]] = None,
        large_threshold: typing.Optional[int] = None,
    ) -> None:
        payload: JSONObject = {
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

    async def send_resume(self, token: str, session_id: str, sequence: int) -> None:
        payload: JSONObject = {
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
        self,
        guild: SupportsGuildID,
        *,
        query: typing.Optional[str] = None,
        limit: typing.Optional[int] = None,
        presences: typing.Optional[bool] = None,
        users: typing.Optional[typing.Iterable[SupportsUserID]] = None,
        nonce: typing.Optional[typing.Union[str, int]] = None,
    ):
        guild_id = str(self.shard.client.guilds.to_unique(guild))
        data: JSONObject = {'guild_id': guild_id}

        if query is not None:
            if users is not None:
                raise TypeError('query and users are mutually exclusive')

            data['query'] = str(query)

            if limit is not None:
                data['limit'] = int(limit)
            else:
                data['limit'] = 0
        else:
            if users is None:
                raise TypeError('one of (query, users) must be provided')

            data['user_ids'] = {str(self.shard.client.users.to_unique(user)) for user in users}

            if limit is not None:
                data['limit'] = int(limit)

        data['presences'] = bool(presences)

        if nonce is not None:
            nonce = str(nonce)
            if len(nonce.encode('utf-8')) > 32:
                raise TypeError('nonce must be <= 32 bytes')

            data['nonce'] = nonce

        logger.info(f'WebSocket requesting guild members in {guild_id}')
        await self.send_json({'op': ShardOpcode.REQUEST_GUILD_MEMBERS, 'd': data})

    async def update_voice_state(
        self,
        guild: SupportsGuildID,
        channel: SupportsChannelID,
        *,
        mute: bool = False,
        deaf: bool = False,
    ) -> None:
        data: JSONObject = {}

        channel_id = self.shard.client.channels.to_unique(channel) if channel is not None else None
        data['channel_id'] = channel_id

        data['guild_id'] = (
            str(self.shard.client.guilds.to_unique(guild)) if guild is not None else None
        )

        data['self_mute'] = bool(mute)
        data['self_deaf'] = bool(deaf)

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
            try:
                event = json_get(payload, 't', str)
            except TypeError:
                return logger.debug('WebSocket received DISPATCH payload with invalid event name')

            try:
                sequence = json_get(payload, 's', int)
            except TypeError:
                return logger.debug('WebSocket received DISPATCH payload with invalid sequence')

            try:
                event_data = json_get(payload, 'd', JSONObject)
            except TypeError:
                return logger.debug('WebSocket received DISPATCH payload with invalid data')

            await self.shard.on_dispatch(event, sequence, event_data)

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
            try:
                hello_data = json_get(payload, 'd', JSONObject)
            except TypeError:
                return self.shard.state.cancel(ShardCancellationToken.INVALID_HELLO_DATA)

            await self.shard.on_hello(hello_data)

        elif opcode is ShardOpcode.HEARTBEAT_ACK:
            await self.shard.on_heartbeat_ack()

    async def on_binary(self, data: bytes):
        if self.detached:
            return logger.debug('WebSocket received binary but it is detached')

        self.shard.state.cancel(ShardCancellationToken.BINARY_RECEIVED)

    async def on_close(self, data: bytes, code: int):
        if self.detached:
            return logger.debug('WebSocket received close but it is detached')

        self.shard.state.cancel(ShardCancellationToken.CONNECTION_CLOSING, (data, code))

    async def on_closed(self, exc: typing.Optional[BaseException]) -> None:
        if self.detached:
            return logger.debug('WebSocket closed but is is datached')

        self.shard.state.cancel(ShardCancellationToken.CONNECTION_CLOSED, exc)

    def detach(self):
        self.detached = True


class ShardBeater:
    def __init__(self, shard: Shard) -> None:
        self.shard = shard
        self.interval = None

        self.sendtime = float('nan')
        self.acktime = float('nan')
        self.latency = float('nan')

        self.stopping = False

    def beat(self) -> None:
        self.shard.loop.create_task(self.do_beat())

    def calculate_jitter(self) -> float:
        assert self.interval is not None
        return random.random() * self.interval

    async def do_beat(self):
        if not self.stopping and self.shard.ws is not None:
            await self.shard.ws.send_heartbeat()
            self.sendtime = time.monotonic()

            assert self.interval is not None
            self.shard.loop.call_later(self.interval, self.beat)

    def ack(self):
        self.acktime = time.monotonic()
        self.latency = self.acktime - self.sendtime

    def start(self, interval: float) -> None:
        self.interval = interval
        self.shard.loop.call_later(self.calculate_jitter(), self.beat)

    def stop(self):
        self.stopping = True


class ShardState:
    cancellation_queue: asyncio.Queue[typing.Tuple[ShardCancellationToken, typing.Any]]
    hello_future: typing.Optional[asyncio.Future[None]]
    ready_future: typing.Optional[asyncio.Future[None]]

    def __init__(self) -> None:
        self.attempts = 0
        self.cancellation_queue = asyncio.Queue()

        self.sequence = -1
        self.session_id: typing.Optional[str] = None
        self.guilds: typing.Dict[str, ShardGuildStatus] = {}

        self.hello_future = None
        self.ready_future = None

        self.last_attempt = float('inf')

        self.stopping = False

    def has_cancellation(self) -> bool:
        return not self.cancellation_queue.empty()

    async def get_cancellation(self) -> typing.Tuple[ShardCancellationToken, typing.Any]:
        return await self.cancellation_queue.get()

    def set_guild_status(self, guild_id: str, status: ShardGuildStatus) -> None:
        self.guilds[guild_id] = status

    def get_guild_status(self, guild_id: str) -> typing.Optional[ShardGuildStatus]:
        return self.guilds.get(guild_id)

    def remove_guild_status(self, guild_id: str) -> typing.Optional[ShardGuildStatus]:
        return self.guilds.pop(guild_id, None)

    def set_hello(self) -> None:
        if self.hello_future is None:
            return None

        with contextlib.suppress(asyncio.InvalidStateError):
            self.hello_future.set_result(None)

    def set_ready(self) -> None:
        if self.ready_future is None:
            return None

        with contextlib.suppress(asyncio.InvalidStateError):
            self.ready_future.set_result(None)

    @contextlib.asynccontextmanager
    async def new_attempt(self) -> typing.AsyncIterator[None]:
        if time.monotonic() - self.last_attempt < 5:
            await asyncio.sleep(1 + random.random() * self.attempts)
        else:
            self.attempts = 0

        self.hello_future = asyncio.Future()
        self.ready_future = asyncio.Future()

        self.attempts += 1
        self.last_attempt = time.monotonic()

        try:
            yield
        except PendingCancellationError:
            if not self.has_cancellation():
                raise RuntimeError(
                    'PendingCancellationError was raised but there is no cancellation pending'
                ) from None

    def cancel(self, token: ShardCancellationToken, info: typing.Any = None) -> None:
        if token is ShardCancellationToken.SIGNAL_INTERRUPT:
            self.stopping = True

        self.cancellation_queue.put_nowait((token, info))

        if self.hello_future is not None:
            with contextlib.suppress(asyncio.InvalidStateError):
                self.hello_future.set_exception(PendingCancellationError)

        if self.ready_future is not None:
            with contextlib.suppress(asyncio.InvalidStateError):
                self.ready_future.set_exception(PendingCancellationError)


class Shard:
    def __init__(
        self, client: WebSocketClient, url: str, shard_id: int, *, sharded: bool = False
    ) -> None:
        self.client = client
        self.url = url
        self.shard_id = shard_id
        self.sharded = sharded

        self.token = self.client.authorization.token
        self.intents = self.client.intents
        self.loop = self.client.loop

        self.ws = None
        self.beater = None

        self.state = ShardState()

        self.task = None
        self.reconnect = False

    @property
    def latency(self) -> float:
        if self.beater is None:
            return float('nan')

        return self.beater.latency

    def create_websocket(self) -> ShardWebSocket:
        return ShardWebSocket(self)

    def create_beater(self) -> ShardBeater:
        return ShardBeater(self)

    def get_identify_properties(self) -> JSONObject:
        return {'$os': platform.system(), '$browser': 'snekcord', '$device': 'snekcord'}

    async def create_connection(self, *, reconnect: bool = False) -> None:
        async with self.state.new_attempt():
            assert self.state.ready_future is not None and self.state.hello_future is not None

            self.ws = self.create_websocket()
            self.beater = self.create_beater()

            try:
                await self.ws.connect(self.url)
            except wsaio.HandshakeFailureError:
                return self.state.cancel(ShardCancellationToken.HANDSHAKE_FAILED)

            try:
                await asyncio.wait_for(self.state.hello_future, 30)
            except asyncio.TimeoutError:
                return self.state.cancel(ShardCancellationToken.HELLO_TIMEOUT)

            if reconnect and self.state.session_id is not None:
                await self.ws.send_resume(self.token, self.state.session_id, self.state.sequence)
            else:
                shard = (self.shard_id, len(self.client.shard_ids)) if self.sharded else None

                await self.ws.send_identify(
                    self.token, self.get_identify_properties(), self.intents, shard=shard
                )

            try:
                await asyncio.wait_for(self.state.ready_future, 30)
            except asyncio.TimeoutError:
                return self.state.cancel(ShardCancellationToken.READY_TIMEOUT)

    async def on_hello(self, data: JSONObject) -> None:
        self.state.set_hello()

        interval = data.get('heartbeat_interval')
        if not isinstance(interval, int):
            self.state.cancel(ShardCancellationToken.INVALID_HEARTBEAT_INTERVAL)
        else:
            assert self.beater is not None
            self.beater.start(interval / 1000)

    async def on_heartbeat_ack(self) -> None:
        assert self.beater is not None
        self.beater.ack()

    async def on_dispatch(self, event: str, sequence: int, data: JSONObject) -> None:
        if sequence > self.state.sequence:
            self.state.sequence = sequence

        if event == 'READY':
            try:
                self.state.session_id = json_get(data, 'session_id', str)
            except TypeError:
                logger.debug('WebSocket received READY payload with invalid session_id')

            try:
                user = json_get(data, 'user', JSONObject)
            except TypeError:
                logger.debug('WebSocket received HELLO payload with invalid user')
            else:
                await self.client.users.upsert(user)

            try:
                guilds = json_get(data, 'guilds', list[JSONObject])
            except TypeError:
                logger.debug('WebSocket received HELLO payload with invalid guilds')
            else:
                for guild in guilds:
                    guild_id = guild.get('id')

                    if isinstance(guild_id, str):
                        self.state.set_guild_status(guild_id, ShardGuildStatus.UNKNOWN)

            return self.state.set_ready()

        if event == 'RESUMED':
            return self.state.set_ready()

        if event == 'GUILD_CREATE':
            guild_id = json_get(data, 'id', str)

            state = self.state.get_guild_status(guild_id)
            if state is None:
                event = 'GUILD_JOIN'
            elif state is ShardGuildStatus.UNAVAILABLE:
                event = 'GUILD_AVAILABLE'
            else:
                event = 'GUILD_RECEIVE'

            self.state.set_guild_status(guild_id, ShardGuildStatus.AVAILABLE)

        elif event == 'GUILD_DELETE':
            guild_id = json_get(data, 'id', str)

            if data.get('unavailable', False):
                event = 'GUILD_UNAVAILABLE'
                self.state.set_guild_status(guild_id, ShardGuildStatus.UNAVAILABLE)
            else:
                self.state.remove_guild_status(guild_id)

        state = self.client.get_event(event)
        if state is not None:
            await state.dispatch(event, self, data)
        else:
            logger.debug(f'WebSocket received unhandled event {event!r}')

    async def on_reconnect(self) -> None:
        self.state.cancel(ShardCancellationToken.RECONNECT_RECEIVED)

    async def on_invalid_session(self, reconnect: bool) -> None:
        self.state.cancel(ShardCancellationToken.INVALID_SESSION, reconnect)

    async def send_close(self, token: ShardCancellationToken, info: typing.Any) -> bool:
        assert self.ws is not None

        if self.ws.is_closing():
            return False

        if token is ShardCancellationToken.HANDSHAKE_FAILED:
            logger.warning('Shard closing due to handshake failure')
            return False

        elif token is ShardCancellationToken.HELLO_TIMEOUT:
            logger.warning('Shard closing because HELLO was not sent in time')
            await self.ws.close(code=wsaio.WebSocketCloseCode.POLICY_VIOLATION)

        elif token is ShardCancellationToken.READY_TIMEOUT:
            logger.warning('Shard closing because READY was not sent in time')
            await self.ws.close(code=wsaio.WebSocketCloseCode.POLICY_VIOLATION)

        if token is ShardCancellationToken.INVALID_HEARTBEAT_INTERVAL:
            logger.warning('Shard closing due to invalid hearbeat interval')
            await self.ws.close(code=wsaio.WebSocketCloseCode.POLICY_VIOLATION)

        elif token is ShardCancellationToken.INVALID_HELLO_DATA:
            logger.warning('Shard closing due to invalid HELLO data')
            await self.ws.close(code=wsaio.WebSocketCloseCode.POLICY_VIOLATION)

        elif token is ShardCancellationToken.RECONNECT_RECEIVED:
            self.reconnect = True

            logger.debug('Shard closing because a RECONNECT was issued')
            await self.ws.close(code=wsaio.WebSocketCloseCode.NORMAL_CLOSURE)

        elif token is ShardCancellationToken.BINARY_RECEIVED:
            logger.warning('Shard closing due to binary data')
            await self.ws.close(code=wsaio.WebSocketCloseCode.UNSUPPORTED_DATA)

        elif token is ShardCancellationToken.INVALID_SESSION:
            self.reconnect = info

            logger.debug('Shard closing bacause an INVALID_SESSION was issued')
            await self.ws.close(code=wsaio.WebSocketCloseCode.NORMAL_CLOSURE)

            await asyncio.sleep(1 + random.random() * 5)

        elif token is ShardCancellationToken.SIGNAL_INTERRUPT:
            logger.debug('Shard closing due to a signal interrupt')
            await self.ws.close(code=wsaio.WebSocketCloseCode.NORMAL_CLOSURE)

        elif token is ShardCancellationToken.CONNECTION_CLOSING:
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

        elif token is ShardCancellationToken.CONNECTION_CLOSED:
            logger.debug(f'Shard lost connection: {info!r}')
            return False

        return True

    def start(self) -> None:
        self._task = self.loop.create_task(self.run())

    async def join(self) -> None:
        await self._task

    async def run(self) -> None:
        while not self.state.stopping:
            await self.create_connection(reconnect=self.reconnect)

            if not self.state.has_cancellation():
                latency = time.monotonic() - self.state.last_attempt
                logger.info(f'Shard established WebSocket connection after {latency * 1000:.3f}ms')

            self.reconnect = False

            token, info = await self.state.get_cancellation()
            assert self.ws is not None

            if self.beater is not None:
                self.beater.stop()

            if await self.send_close(token, info):
                with contextlib.suppress(asyncio.TimeoutError):
                    data = await asyncio.wait_for(self.state.get_cancellation(), 10)

                    if data[0] is not ShardCancellationToken.CONNECTION_CLOSING:
                        logger.warning(
                            f'Shard expected CONNECTION_CLOSING token but found '
                            f'{data!r} instead, detaching WebSocket'
                        )
                        self.ws.detach()

            if self.ws.stream is not None:
                try:
                    await self.ws.stream.close()
                except Exception:
                    logger.exception(
                        'Shard failed to close WebSocket due to an exception, ignoring'
                    )

            while self.state.has_cancellation():
                data = await self.state.get_cancellation()
                if data[0] is not ShardCancellationToken.CONNECTION_CLOSED:
                    logger.debug(
                        f'Shard found unhandled token {data!r} in cancellation queue, discarding'
                    )

            if self.state.hello_future is not None:
                self.state.hello_future.cancel()

            if self.state.ready_future is not None:
                self.state.ready_future.cancel()
