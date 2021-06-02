import enum
import json
import platform
import time

from wsaio import taskify

from .basews import BaseWebSocket, WebSocketResponse
from ..utils import Snowflake


class ShardOpcode(enum.IntEnum):
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


class ShardCloseCode(enum.IntEnum):
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


class Shard(BaseWebSocket):
    def __init__(self, worker, shard_id=None, intents=None):
        super().__init__(loop=worker.loop)
        self.worker = worker
        self.id = shard_id
        self.intents = intents

        self.v = None
        self.user = None
        self.startup_guilds = set()
        self.available_guilds = set()
        self.unavailable_guilds = set()
        self.session_id = None
        self.info = None

        self.sequence = -1
        self._chunk_nonce = -1

    def _remove_startup_guild(self, guild_id):
        try:
            self.startup_guilds.remove(guild_id)
        except KeyError:
            pass

        if self.ready.is_set():
            if not self.startup_guilds:
                self.worker.manager.dispatch('SHARD_READY', self)

    async def identify(self):
        payload = {
            'op': ShardOpcode.IDENTIFY,
            'd': {
                'token': self.worker.manager.token,
                # 'intents': self.intents,
                'properties': {
                    '$os': platform.system(),
                    '$browser': 'snekcord',
                    '$device': 'snekcord'
                }
            }
        }
        await self.send_str(json.dumps(payload))

    async def resume(self):
        payload = {
            'op': ShardOpcode.RESUME,
            'd': {
                'token': self.manager.token,
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

        try:
            opcode = ShardOpcode(response.opcode)
        except ValueError:
            return

        if (response.sequence is not None
                and response.sequence > self.sequence):
            self.sequence = response.sequence

        if opcode is ShardOpcode.DISPATCH:
            if response.name == 'READY':
                self.v = response.data['v']
                self.user = self.worker.manager.users.upsert(
                    response.data['user'])
                self.session_id = response.data['session_id']
                self.info = response.data.get('shard')

                for guild in response.data['guilds']:
                    guild_id = guild['id']
                    self.startup_guilds.add(guild_id)
                    self.available_guilds.add(guild_id)

                self.ready.set()

            elif response.name == 'GUILD_DELETE':
                guild_id = response.data['id']

                self._remove_startup_guild(guild_id)

                if data['unavailable']:
                    try:
                        self.available_guilds.remove(guild_id)
                    except KeyError:
                        pass

                    self.unavailable_guilds.add(guild_id)

                    self.worker.manager.dispatch(
                        'GUILD_UNAVAILABLE', self, response.data)
                else:
                    try:
                        self.available_guilds.remove(guild_id)
                    except KeyError:
                        pass

                    try:
                        self.unavailable_guilds.remove(guild_id)
                    except KeyError:
                        pass

                    self.worker.manager.dispatch(
                        'GUILD_DELETE', self, response.data)

            elif response.name == 'GUILD_CREATE':
                guild_id = response.data['id']

                self._remove_startup_guild(guild_id)

                if guild_id in self.available_guilds:
                    self.worker.manager.dispatch(
                        'GUILD_RECEIVE', self, response.data)
                else:
                    self.available_guilds.add(guild_id)

                    if guild_id in self.unavailable_guilds:
                        self.unavailable_guilds.remove(guild_id)
                        self.worker.manager.dispatch(
                            'GUILD_AVAILABLE', self, response.data)

                    else:
                        self.worker.manager.dispatch(
                            'GUILD_JOIN', self, response.data)

            else:
                self.worker.manager.dispatch(
                    response.name, self, response.data)

        elif opcode is ShardOpcode.HEARTBEAT:
            await self.send_heartbeat()

        elif opcode is ShardOpcode.RECONNECT:
            return

        elif opcode is ShardOpcode.INVALID_SESSION:
            return

        elif opcode is ShardOpcode.HELLO:
            self.heartbeat_interval = (
                response.data['heartbeat_interval'] / 1000)
            self.worker.notifier.register(self, self.heartbeat_interval)
            await self.identify()

        elif opcode is ShardOpcode.HEARTBEAT_ACK:
            self.worker.ack(self)
