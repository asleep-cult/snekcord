from __future__ import annotations

import asyncio
import enum
import platform
import random
import time

from loguru import logger

from wsaio import (
    HandshakeFailureError,
    WS_NORMAL_CLOSURE,
    WS_POLICY_VIOLATION,
    WS_UNSUPPORTED_DATA,
    WebSocketClient,
)

from ..builders import JSONBuilder
from ..exceptions import ShardConnectError
from ..json import dump_json, load_json
from ..states import (
    ChannelState,
    GuildState,
    UserState,
)
from ..undefined import undefined

__all__ = (
    'ShardOpcode',
    'ShardCloseCode',
    'ShardWebSocket',
    'ShardWebSocketClient',
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


class _ShardGuildState(enum.IntEnum):
    UNKNOWN = enum.auto()
    AVAILABLE = enum.auto()
    UNAVAILABLE = enum.auto()


class ShardHeartbeater:
    def __init__(self, shard):
        self.shard = shard
        self.interval = None

        self.sendtime = float('nan')
        self.acktime = float('nan')
        self.latency = float('nan')

        self.stopping = False

    def create_task(self):
        return self.shard.loop.create_task(self.send_heartbeat())

    def calculate_jitter(self):
        return random.random() * self.interval

    async def send_heartbeat(self):
        if not self.stopping:
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


class ShardWebSocket:
    def __init__(self, client, url):
        self.client = client
        self.url = url

        self.ws = None
        self.heartbeater = None

        self._sequence = -1
        self._session_id = None
        self._reconnect = None
        self._guild_states = {}
        self._hello_ev = asyncio.Event()
        self._ready_ev = asyncio.Event()

    @property
    def token(self):
        return self.client.authorization.token

    @property
    def intents(self):
        return self.client.get_intents()

    @property
    def loop(self):
        return self.client.loop

    @property
    def latency(self):
        if self.heartbeater is None:
            return float('nan')
        return self.heartbeater.latency

    def create_websocket(self):
        self.ws = ShardWebSocketClient(self)

    def create_heartbeater(self):
        self.heartbeater = ShardHeartbeater(self)

    def should_reconnect(self):
        return self._session_id is not None and self._reconnect is not False

    def get_identify_properties(self):
        return {'$os': platform.system(), '$browser': 'snekcord', '$device': 'snekcord'}

    async def wait_for_hello(self):
        await asyncio.wait_for(self._hello_ev.wait(), timeout=30)

    async def wait_for_ready(self):
        await asyncio.wait_for(self._ready_ev.wait(), timeout=30)

    async def on_hello(self, data):
        self._hello_ev.set()

        interval = data.get('heartbeat_interval')
        if not isinstance(interval, int):
            await self.ws.close('WebSocket received HELLO payload with invalid heartbeat_interval')

        self.heartbeater.start(interval / 1000)

    async def on_heartbeat_ack(self):
        self.heartbeater.ack()

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
                    self._guild_states[guild['id']] = _ShardGuildState.UNKNOWN

            self._ready_ev.set()
        elif event == 'RESUMED':
            self._ready_ev.set()
        else:
            if event == 'GUILD_CREATE':
                guild_id = data['id']

                state = self._guild_states.get(guild_id)
                if state is None:
                    event = 'GUILD_JOIN'
                elif state is _ShardGuildState.UNAVAILABLE:
                    event = 'GUILD_AVAILABLE'
                else:
                    event = 'GUILD_RECEIVE'

                self._guild_states[guild_id] = _ShardGuildState.AVAILABLE

            elif event == 'GUILD_DELETE':
                guild_id = data['id']

                if data.get('unavailable', False):
                    event = 'GUILD_UNAVAILABLE'
                    self._guild_states[guild_id] = _ShardGuildState.UNAVAILABLE
                else:
                    self._guild_states.pop(guild_id, None)

            listener = self.client.get_listener_for(event)
            if listener is not None:
                await listener.dispatch(event, data)
            else:
                logger.debug(f'WebSocket received unknown event {event!r}')

    async def on_reconnect(self):
        await self.ws.close('WebSocket requested reconnect', code=WS_NORMAL_CLOSURE)

    async def on_invalid_session(self, reconnect):
        self._reconnect = reconnect

    async def on_close(self, code, data):
        self._hello_ev.clear()
        self._ready_ev.clear()

    async def connect(self):
        self.create_websocket()
        self.create_heartbeater()

        self._guild_states.clear()

        try:
            await self.ws.connect(self.url)
        except HandshakeFailureError:
            raise ShardConnectError('WebSocket failed to complete handshake')

        try:
            await self.wait_for_hello()
        except asyncio.TimeoutError:
            await self.ws.close('WebSocket failed to send HELLO in time', code=WS_POLICY_VIOLATION)
            raise ShardConnectError(self, 'WebSocket timed out while waiting for HELLO')

        if self.should_reconnect():
            self._reconnect = False
            await self.ws.send_resume(self.token, self._session_id, self._sequence)
        else:
            await self.ws.send_identify(self.token, self.get_identify_properties(), self.intents)

        try:
            await self.wait_for_ready()
        except asyncio.TimeoutError:
            await self.ws.close(
                'WebSocket failed to send READY/RESUMED in time', code=WS_POLICY_VIOLATION
            )
            raise ShardConnectError(self, 'WebSocket timed out while waiting for READY/RESUMED')

        self._reconnect = None

        return self


class ShardWebSocketClient(WebSocketClient):
    def __init__(self, shard: ShardWebSocket) -> None:
        super().__init__(loop=shard.loop)
        self.shard = shard

    async def send_json(self, data):
        await self.write(dump_json(data))

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

        guild_id = GuildState.unwrap_id(guild)
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
                user_ids.add(UserState.unwrap_id(user))

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

        data.snowflake('guild_id', GuildState.unwrap_id(guild))

        if channel is not None:
            channel = ChannelState.unwrap_id(channel)

        channel_id = ChannelState.unwrap_id(channel)
        data.snowflake('channel_id', channel_id, nullable=True)

        data.bool('self_mute', mute)
        data.bool('self_deaf', deaf)

        logger.info(f'WebSocket updating voice state in {channel_id}')
        await self.send_json({'op': ShardOpcode.VOICE_STATE_UPDATE, 'd': data})

    async def on_text(self, data: str) -> None:
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
                return await self.close(
                    'WebSocket received HELLO payload with invalid data', code=WS_POLICY_VIOLATION
                )

            await self.shard.on_hello(data)

        elif opcode is ShardOpcode.HEARTBEAT_ACK:
            await self.shard.on_heartbeat_ack()

    async def on_binary(self, data):
        await self.close('WebSocket received binary frame', code=WS_UNSUPPORTED_DATA)

    async def on_close(self, code, data):
        logger.warning(f'WebSocket is closing [{code}]: {data}')
        await self.shard.on_close(code, data)
