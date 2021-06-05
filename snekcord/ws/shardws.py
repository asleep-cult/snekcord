import asyncio
import json
import platform
import random
import time

from wsaio import taskify

from .basews import BaseWebSocket, WebSocketResponse
from ..utils import Enum, Snowflake


class ShardOpcode(Enum, type=int):
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


class ShardCloseCode(Enum, type=int):
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


class Shard:
    def __init__(self, *, manager, shard_id):
        self.manager = manager

        self.id = shard_id
        self.count = self.manager.shard_count

        self.loop = self.manager.loop
        self.token = self.manager.token
        self.intents = self.manager.intents

        self.callbacks = {
            'HELLO': self.on_hello,
            'READY': self.on_ready,
            'DISPATCH': self.on_dispatch,
            'GUILDS_RECEIVED': self.on_guilds_received,
            'CLOSED': self.on_closed,
            'CLOSING': self.on_closing,
            'CONNECTION_LOST': self.on_connection_lost
        }

        self.create_ws(reconnect=False)

    def create_ws(self, *, reconnect=True):
        if not reconnect:
            self.session_id = None
            self.available_guilds = set()
            self.unavailable_guilds = set()
            self.sequence = -1
        else:
            self.session_id = self.ws.session_id
            self.sequence = self.ws.sequence

        self.ws = ShardWebSocket(self.id, self.count, loop=self.loop,
                                 token=self.token, intents=self.intents,
                                 callbacks=self.callbacks,
                                 session_id=self.session_id,
                                 available_guilds=self.available_guilds,
                                 unavailable_guilds=self.unavailable_guilds,
                                 sequence=self.sequence)

        self.heartbeater_task = None

    @property
    def latency(self):
        return self.ws.latency

    async def on_hello(self):
        self.heartbeater_task = self.loop.create_task(self.heartbeater())

    async def on_ready(self, data):
        self.user = self.manager.users.upsert(data['user'])

    async def on_dispatch(self, name, data):
        await self.manager.dispatch(name, self, data)

    async def on_guilds_received(self):
        await self.manager.dispatch('SHARD_READY', self)

    async def on_closed(self, code, data):
        print(f'SHARD {self.id} DIED. {code}, {data}')

    async def on_closing(self, exc):
        print(f'SHARD {self.id} DIED. {exc}')

    async def on_connection_lost(self, exc):
        print(f'SHARD {self.id} LOST CONNECTION. {exc}')

    async def heartbeater(self):
        delay = (random.random() * self.ws.heartbeat_interval) / 1000
        await asyncio.sleep(delay)

        heartbeat_interval = self.ws.heartbeat_interval / 1000
        while True:
            await self.ws.send_heartbeat()
            await asyncio.sleep(heartbeat_interval)

    async def connect(self, *args, **kwargs):
        await self.ws.connect(*args, **kwargs)


class ShardWebSocket(BaseWebSocket):
    def __init__(self, shard_id, shard_count, *, loop, token, intents,
                 callbacks, session_id=None, available_guilds=None,
                 unavailable_guilds=None, sequence=-1):
        super().__init__(loop=loop)
        self.id = shard_id
        self.count = shard_count
        self.token = token
        self.intents = intents
        self.callbacks = callbacks

        self.v = None
        self.info = None
        self.session_id = session_id
        self.startup_guilds = set()

        if unavailable_guilds is not None:
            self.unavailable_guilds = unavailable_guilds
        else:
            self.unavailable_guilds = set()

        if available_guilds is not None:
            self.available_guilds = available_guilds
        else:
            self.available_guilds = set()

        self.sequence = sequence
        self._chunk_nonce = -1

    @property
    def shard(self):
        if self.count is not None:
            return (self.id, self.count)
        return None

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
        await self.callbacks['CONNECTION_LOST'](exc)

    async def _remove_startup_guild(self, guild_id):
        try:
            self.startup_guilds.remove(guild_id)
        except KeyError:
            pass

        if self.ready.is_set():
            if not self.startup_guilds:
                await self.callbacks['GUILDS_RECEIVED']()

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

        shard = self.shard
        if shard is not None:
            payload['shard'] = shard

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

                await self.callbacks['READY'](response.data)
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

            await self.callbacks['DISPATCH'](name, response.data)

        elif opcode == ShardOpcode.HEARTBEAT:
            await self.send_heartbeat()

        elif opcode == ShardOpcode.RECONNECT:
            return

        elif opcode == ShardOpcode.INVALID_SESSION:
            return

        elif opcode == ShardOpcode.HELLO:
            self.heartbeat_interval = response.data['heartbeat_interval']
            await self.callbacks['HELLO']()
            await self.identify()

        elif opcode == ShardOpcode.HEARTBEAT_ACK:
            self.heartbeat_last_acked = time.perf_counter()
