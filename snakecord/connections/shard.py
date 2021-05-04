import enum
import platform

from wsaio import taskify

from .base import BaseConnection, Heartbeater, WebSocketResponse


class ShardOpcode(enum.IntEnum):
    DISPATCH = 0  # Discord -> Shard
    HEARTBEAT = 1  # Discord <-> Shard
    IDENTIFY = 2  # Discord <- Shard
    PRESENCE_UPDATE = 3  # Discord -> Shard
    VOICE_STATE_UPDATE = 4  # Discord -> Shard
    VOICE_SERVER_PING = 5  # Discord ~ Shard
    RESUME = 6  # Discord <- Shard
    RECONNECT = 7  # Discord -> Shard
    REQUEST_GUILD_MEMBERS = 8  # Discord <- Shard
    INVALID_SESSION = 9  # Discord -> Shard
    HELLO = 10  # Discord -> Shard
    HEARTBEAT_ACK = 11  # Discord -> Shard


class Shard(BaseConnection):
    ENDPOINT = 'wss://gateway.discord.gg?v=8'

    def __init__(self, manager, id: int):
        super().__init__(manager)
        self.id = id

    @property
    def heartbeat_payload(self):
        payload = {
            'op': ShardOpcode.HEARTBEAT,
            'd': None
        }
        return payload

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
        await self.send_json(payload)

    @taskify
    async def ws_ping_received(self, data: bytes):
        await self.send_pong(data)

    @taskify
    async def ws_text_received(self, data: str) -> None:
        response = WebSocketResponse.unmarshal(data)
        # response.opcode = ShardOpcode(response.opcode)

        if response.opcode == ShardOpcode.DISPATCH:
            self.manager.dispatch(response.name, self, response.data)
        if response.opcode == ShardOpcode.HELLO:
            self.heartbeater = Heartbeater(
                self, loop=self.loop,
                delay=response.data['heartbeat_interval'] / 1000)
            self.heartbeater.start()
            await self.identify()
        elif response.opcode == ShardOpcode.HEARTBEAT:
            self.send_heartbeat()

    async def connect(self, *args, **kwargs):
        await super().connect(self.ENDPOINT, *args, **kwargs)
