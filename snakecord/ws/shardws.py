import enum
import json
import platform

from wsaio import WebSocketClient, taskify

from .basews import WebSocketResponse
from ..utils import Snowflake


class ShardOpcode(enum.IntEnum):
    DISPATCH = 0  # Discord -> Shard
    HEARTBEAT = 1  # Discord <-> Shard
    IDENTIFY = 2  # Discord <- Shard
    PRESENCE_UPDATE = 3  # Discord <- Shard
    VOICE_STATE_UPDATE = 4  # Discord -> Shard
    VOICE_SERVER_PING = 5  # Discord ~ Shard
    RESUME = 6  # Discord <- Shard
    RECONNECT = 7  # Discord -> Shard
    REQUEST_GUILD_MEMBERS = 8  # Discord <- Shard
    INVALID_SESSION = 9  # Discord -> Shard
    HELLO = 10  # Discord -> Shard
    HEARTBEAT_ACK = 11  # Discord -> Shard


class Shard(WebSocketClient):
    def __init__(self, manager, shard_id):
        super().__init__(loop=manager.loop)
        self.manager = manager
        self.id = shard_id

        self.session_id = None
        self.sequence = -1
        self._chunk_nonce = -1

    async def identify(self):
        payload = {
            'op': ShardOpcode.IDENTIFY,
            'd': {
                'token': self.manager.token,
                'intents': self.manager.intents,
                'properties': {
                    '$os': platform.system(),
                    '$browser': 'snakecord',
                    '$device': 'snakecord'
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
        response = await WebSocketResponse.unmarshal(data)

        try:
            opcode = ShardOpcode(response.opcode)
        except ValueError:
            return

        if (
            response.sequence is not None
            and response.sequence > self.sequence
        ):
            self.sequence = response.sequence

        if opcode is ShardOpcode.DISPATCH:
            self.manager.dispatch(response.name, self, response.data)
        elif opcode is ShardOpcode.HEARTBEAT:
            await self.send_heartbeat()
        elif opcode is ShardOpcode.VOICE_STATE_UPDATE:
            return
        elif opcode is ShardOpcode.RECONNECT:
            return
        elif opcode is ShardOpcode.INVALID_SESSION:
            return
        elif opcode is ShardOpcode.HELLO:
            await self.identify()
        elif opcode is ShardOpcode.HEARTBEAT_ACK:
            return
