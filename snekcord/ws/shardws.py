import json
import platform
import random
import time

from wsaio import taskify

from .basews import BaseWebSocket, BaseWebSocketWorker, WebSocketResponse
from ..utils import Enum, Snowflake


class ShardOpcode(Enum):
    __enum_type__ = int

    DISPATCH = 0  # Discord -> Shard
    HEARTBEAT = 1  # Discord <-> Shard
    IDENTIFY = 2  # Discord <- Shard
    PRESENCE_UPDATE = 3  # Discord <- Shard
    VOICE_STATE_UPDATE = 4  # Discord <- Shard
    VOICE_SERVER_PING = 5  # Discord ~ Shard
    RESUME = 6  # Discord <- Shard
    RECONNECT = 7  # Discord -> Shard
    REQUEST_GUILD_MEMBERS = 8  # Discord <- Shard
    INVALID_SESSION = 9  # Discord -> Shard
    HELLO = 10  # Discord -> Shard
    HEARTBEAT_ACK = 11  # Discord -> Shard


class ShardCloseCode(Enum):
    __enum_type__ = int

    UNKNOWN_ERROR = 4000
    UNKNOWN_OPCODE = 4001
    DECODE_ERROR = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    INVALID_SEQUENCE = 4007
    RATE_LIMITED = 4008
    SESSION_TIMED_OUT = 4009
    INVALID_SHARD = 4010
    SHARDING_REQUIRED = 4011
    INVALID_API_VERSION = 4012
    INVALID_INTENTS = 4013
    DISALLOWED_INTENTS = 4014


class Sharder(BaseWebSocketWorker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.user = None
        self.shards = {}

    async def _op_hello(self, shard):
        delay = (random.random() * shard.heartbeat_interval) / 1000
        # https://discord.com/developers/docs/topics/gateway#heartbeating
        self.loop.call_later(delay, self.notifier.register,
                             shard, shard.heartbeat_interval / 1000)

    async def _op_dispatch(self, shard, name, data):
        await self.manager.dispatch(name, shard, data)

    async def _op_heartbeat_ack(self, shard):
        self.ack(shard)

    async def _event_ready(self, shard, data):
        self.user = self.manager.users.upsert(data['user'])

    async def _event_guilds_received(self, shard):
        await self.manager.dispatch('SHARD_READY', shard)

    async def create_connection(self, shard_id, *args, **kwargs):
        callbacks = {
            'HELLO': self._op_hello,
            'DISPATCH': self._op_dispatch,
            'HEARTBEAT_ACK': self._op_heartbeat_ack,
            'READY': self._event_ready,
            'GUILDS_RECEIVED': self._event_guilds_received
        }
        shard = ShardWebSocket(shard_id, loop=self.loop,
                               token=kwargs.pop('token'),
                               intents=kwargs.pop('intents'),
                               callbacks=callbacks)

        await shard.connect(*args, **kwargs)

        return shard


class ShardWebSocket(BaseWebSocket):
    def __init__(self, shard_id, *, loop, token, intents, callbacks):
        super().__init__(loop=loop)
        self.id = shard_id
        self.token = token
        self.intents = intents
        self.callbacks = callbacks
        # HELLO: We received opcode HELLO from Discord
        # (start sending heartbeats)
        # READY: We received READY from Discord
        # DISPATCH: We received opcode DISPATCH from Discord
        # HEARTBEAT_ACK: We received opcode HEARTBEAT_ACK from Discord
        # GUILDS_RECEIVED: We received all the guilds we needed to
        # CLOSED: We received a close frame from Discord
        # CLOSING: We sent a close frame to Discord
        # CONNECTION_LOST: The connection was lost, we're officially dead

        self.v = None
        self.startup_guilds = set()
        self.available_guilds = set()
        self.unavailable_guilds = set()
        self.session_id = None
        self.info = None

        self.sequence = -1
        self._chunk_nonce = -1

    @taskify
    async def closing_connection(self, exc):
        super().closing_connection(exc)
        await self.callbacks['CLOSING'](exc)

    @taskify
    async def ws_close_received(self, code, data):
        super().ws_close_received(code, data)
        await self.callbacks['CLOSED'](code, data)

    @taskify
    async def connection_lost(self, exc):
        super().connection_lost(exc)
        await self.callbacks['CONNECTION_LOST'](self, exc)

    async def _remove_startup_guild(self, guild_id):
        try:
            self.startup_guilds.remove(guild_id)
        except KeyError:
            pass

        if self.ready.is_set():
            if not self.startup_guilds:
                await self.callbacks['GUILDS_RECEIVED'](self)

    async def identify(self):
        payload = {
            'op': ShardOpcode.IDENTIFY,
            'd': {
                'token': self.token,
                'properties': {
                    '$os': platform.system(),
                    '$browser': 'snekcord',
                    '$device': 'snekcord'
                }
            }
        }

        if self.intents is not None:
            payload['intents'] = int(self.intents)

        await self.send_str(json.dumps(payload))

    async def resume(self):
        payload = {
            'op': ShardOpcode.RESUME,
            'd': {
                'token': self.token,
                'session_id': self.session_id,
                'seq': self.sequence
            }
        }
        await self.send_str(json.dumps(payload))

    async def send_heartbeat(self):
        payload = {
            'op': ShardOpcode.HEARTBEAT,
            'd': None
        }
        await self.send_str(json.dumps(payload))
        self.heartbeat_last_sent = time.perf_counter()

    async def request_guild_members(self, guild, presences=None, limit=None,
                                    users=None, query=None):
        payload = {
            'op': ShardOpcode.REQUEST_GUILD_MEMBERS,
            'guild_id': Snowflake.try_snowflake(guild)
        }

        if presences is not None:
            payload['presences'] = presences

        if query is not None:
            payload['query'] = query

            if limit is not None:
                payload['limit'] = limit
            else:
                payload['limit'] = 0
        elif users is not None:
            payload['user_ids'] = tuple(Snowflake.try_snowflake_set(users))

            if limit is not None:
                payload['limit'] = limit

        self._chunk_nonce += 1

        if self._chunk_nonce >= 1 << 32:
            # nonce counts up to a 32 bit integer
            self._chunk_nonce = 0

        payload['nonce'] = str(self._chunk_nonce)

        await self.send_str(json.dumps(payload))

    @taskify
    async def ws_text_received(self, data):
        response = WebSocketResponse.unmarshal(data)
        opcode = ShardOpcode.get_enum(response.opcode)

        if (response.sequence is not None
                and response.sequence > self.sequence):
            self.sequence = response.sequence

        if opcode == ShardOpcode.DISPATCH:
            name = response.name

            if name == 'READY':
                self.v = response.data['v']
                self.session_id = response.data['session_id']
                self.info = response.data.get('shard')

                for guild in response.data['guilds']:
                    guild_id = guild['id']
                    self.startup_guilds.add(guild_id)
                    self.available_guilds.add(guild_id)

                await self.callbacks['READY'](self, response.data)
                return
            elif name == 'GUILD_DELETE':
                guild_id = response.data['id']

                await self._remove_startup_guild(guild_id)

                if data['unavailable']:
                    try:
                        self.available_guilds.remove(guild_id)
                    except KeyError:
                        pass

                    self.unavailable_guilds.add(guild_id)

                    name = 'GUILD_UNAVAILABLE'
                else:
                    try:
                        self.available_guilds.remove(guild_id)
                    except KeyError:
                        pass

                    try:
                        self.unavailable_guilds.remove(guild_id)
                    except KeyError:
                        pass
            elif name == 'GUILD_CREATE':
                guild_id = response.data['id']

                await self._remove_startup_guild(guild_id)

                if guild_id in self.available_guilds:
                    name = 'GUILD_RECEIVE'
                else:
                    self.available_guilds.add(guild_id)

                    if guild_id in self.unavailable_guilds:
                        self.unavailable_guilds.remove(guild_id)
                        name = 'GUILD_AVAILABLE'
                    else:
                        name = 'GUILD_JOIN'

            await self.callbacks['DISPATCH'](self, name, response.data)

        elif opcode == ShardOpcode.HEARTBEAT:
            await self.send_heartbeat()

        elif opcode == ShardOpcode.RECONNECT:
            return

        elif opcode == ShardOpcode.INVALID_SESSION:
            return

        elif opcode == ShardOpcode.HELLO:
            self.heartbeat_interval = response.data['heartbeat_interval']
            await self.callbacks['HELLO'](self)
            await self.identify()

        elif opcode == ShardOpcode.HEARTBEAT_ACK:
            await self.callbacks['HEARTBEAT_ACK'](self)
