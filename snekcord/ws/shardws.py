import asyncio
import json
import platform
import random
import time

from .basews import BaseWebSocket, WebSocketResponse
from ..utils import Snowflake

__all__ = ('ShardOpcode', 'ShardCloseCode', 'Shard', 'ShardWebSocket')


class ShardOpcode:
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


class ShardCloseCode:
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
    def __init__(self, *, shard_id, client):
        self.id = shard_id
        self.client = client

        self._callbacks = {
            'HELLO': self.on_hello,
            'READY': self.on_ready,
            'GUILDS_RECEIVED': self.on_guilds_received,
            'DISPATCH': self.on_dispatch,
            'CLOSED': self.on_closed,
            'CLOSING': self.on_closing,
            'CONNECTION_LOST': self.on_connection_lost,
        }

        self.create_ws()

    @property
    def latency(self):
        return self.ws.latency

    def create_ws(self):
        self.ws = ShardWebSocket(
            self.id, self.client.shard_count, loop=self.client.loop,
            token=self.client.authorization.token, intents=self.client.intents,
            callbacks=self._callbacks
        )

        self.user = None
        self.heartbeater_task = None

    async def on_hello(self):
        self.heartbeater_task = self.client.loop.create_task(self._heartbeater())

    async def on_ready(self, data):
        self.user = self.client.users.upsert(data['user'])

    async def on_guilds_received(self):
        await self.client.dispatch('SHARD_READY', self)

    async def on_dispatch(self, name, data):
        await self.client.dispatch(name, self, data)

    async def on_closed(self, code, data):
        print(f'SHARD {self.id} DIED. {code}, {data}')

    async def on_closing(self, exc):
        print(f'SHARD {self.id} DIED. {exc}')

    async def on_connection_lost(self, exc):
        print(f'SHARD {self.id} LOST CONNECTION. {exc}')

    async def on_connection_lost(self, exc):
        print(f'SHARD {self.id} LOST CONNECTION. {exc}')

    async def _heartbeater(self):
        heartbeat_interval = self.ws.heartbeat_interval / 1000

        await asyncio.sleep(random.random() * heartbeat_interval)

        while True:
            await self.ws.send_heartbeat()
            await asyncio.sleep(heartbeat_interval)


class ShardWebSocket(BaseWebSocket):
    def __init__(self, shard_id, shard_count, *, loop=None, token, intents, callbacks):
        super().__init__(loop=loop)
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.token = token
        self.intents = intents
        self.callbcks = callbacks

        self.version = None
        self.shard_info = None
        self.session_id = None

        self.startup_guilds = set()
        self.available_guilds = set()
        self.unavailable_guilds = set()

        self.sequence = -1

        self._ready = False
        self._guilds_received = False

    def closing_connection(self, exc):
        super().closing_connection(exc)
        self.loop.create_task(self.callbcks['CLOSING'](exc))

    def ws_close_received(self, code, data):
        super().ws_close_received(code, data)
        self.loop.create_task(self.callbcks['CLOSED'](code, data))

    def connection_lost(self, exc):
        super().connection_lost(exc)
        self.loop.create_task(self.callbcks['CONNECTION_LOST'](exc))

    def _remove_startup_guild(self, guild_id):
        try:
            self.startup_guilds.remove(guild_id)
        except KeyError:
            pass

        if self._ready and not self._guilds_received and not self.startup_guilds:
            self.loop.create_task(self.callbcks['GUILDS_RECEIVED']())

    def _add_available_guild(self, guild_id):
        self._remove_startup_guild(guild_id)

        try:
            self.unavailable_guilds.remove(guild_id)
        except KeyError:
            pass

        self.available_guilds.add(guild_id)

    def _add_unavailable_guild(self, guild_id):
        self._remove_startup_guild(guild_id)

        try:
            self.available_guilds.remove(guild_id)
        except KeyError:
            pass

        self.unavailable_guilds.add(guild_id)

    def _purge_guild(self, guild_id):
        self._remove_startup_guild(guild_id)

        try:
            self.available_guilds.remove(guild_id)
        except KeyError:
            pass

        try:
            self.unavailable_guilds.remove(guild_id)
        except KeyError:
            pass

    async def send_heartbeat(self):
        payload = {
            'op': ShardOpcode.HEARTBEAT,
            'd': None
        }

        await self.send_str(json.dumps(payload))

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
            payload['d']['intents'] = int(self.intents)

        if self.shard_count != 1:
            payload['d']['shard'] = (self.shard_id, self.shard_count)

        await self.send_str(json.dumps(payload))

    async def resume(self):
        payload = {
            'op': ShardOpcode.RESUME,
            'd': {
                'token': self.token,
                'session_id': self.session_id,
                'seq': self.sequence,
            }
        }

        await self.send_str(json.dumps(payload))

        self.heartbeat_last_sent = time.perf_counter()

    async def resuest_guild_members(
        self, guild, presences=None, limit=None, users=None, query=None
    ):
        payload = {
            'op': ShardOpcode.REQUEST_GUILD_MEMBERS,
            'guild_id': Snowflake.try_snowflake(guild)
        }

        if presences is not None:
            payload['presences'] = int(presences)

        if query is not None:
            payload['query'] = str(query)

            if limit is not None:
                payload['limit'] = int(limit)
            else:
                payload['limit'] = 0
        elif users is not None:
            payload['user_ids'] = Snowflake.try_snowflake_many(users)

            if limit is not None:
                payload['limit'] = int(limit)

        await self.send_str(json.dumps(payload))

    def ws_text_received(self, data):
        response = WebSocketResponse.unmarshal(data)

        if response.sequence is not None and response.sequence > self.sequence:
            self.sequence = response.sequence

        if response.opcode == ShardOpcode.DISPATCH:
            name = response.name

            if name == 'READY':
                self.version = response.data['v']
                self.session_id = response.data['session_id']
                self.shard_info = response.data.get('shard')

                for guild in response.data['guilds']:
                    guild_id = guild['id']

                    self.startup_guilds.add(guild_id)

                self._ready = True

                self.loop.create_task(self.callbcks['READY'](response.data))
            elif name == 'GUILD_CREATE':
                guild_id = response.data['id']

                from_unavailable = guild_id in self.unavailable_guilds
                joined = (
                    not from_unavailable
                    and guild_id not in self.startup_guilds
                    and guild_id not in self.available_guilds
                )

                response.data['_from_unavailable_'] = from_unavailable
                response.data['_joined_'] = joined

                self._add_available_guild(guild_id)
            elif name == 'GUILD_DELETE':
                guild_id = response.data['id']

                if response.data.get('unavailable', False):
                    name = 'GUILD_UNAVAILABLE'
                    self._add_available_guild(guild_id)
                else:
                    self._purge_guild(guild_id)

            self.loop.create_task(self.callbcks['DISPATCH'](name, response.data))

        elif response.opcode == ShardOpcode.HEARTBEAT:
            self.loop.create_task(self.send_heartbeat())

        elif response.opcode == ShardOpcode.RECONNECT:
            pass

        elif response.opcode == ShardOpcode.INVALID_SESSION:
            pass

        elif response.opcode == ShardOpcode.HELLO:
            self.heartbeat_interval = response.data['heartbeat_interval']

            self.loop.create_task(self.identify())
            self.loop.create_task(self.callbcks['HELLO']())

        elif response.opcode == ShardOpcode.HEARTBEAT_ACK:
            self.heartbeat_last_acked = time.perf_counter()
