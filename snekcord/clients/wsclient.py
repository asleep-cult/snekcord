from .client import Client
from .wsevents import EVENTS
from .. import rest
from ..utils.bitset import Flag, NamedBitset
from ..ws.shardws import Sharder

__all__ = ('WebSocketIntents', 'WebSocketClient')


class WebSocketIntents(NamedBitset):
    guilds = Flag(0)
    guild_members = Flag(1)
    guild_bans = Flag(2)
    guild_emojis = Flag(3)
    guild_integrations = Flag(4)
    guild_webhooks = Flag(5)
    guild_invites = Flag(6)
    guild_voice_states = Flag(7)
    guild_presences = Flag(8)
    guild_messages = Flag(9)
    guild_message_reactions = Flag(10)
    guild_message_typing = Flag(11)
    direct_messages = Flag(12)
    direct_message_reactions = Flag(13)
    direct_message_typing = Flag(14)


class WebSocketClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager.__events__ = EVENTS
        self.sharder = Sharder(manager=self.manager, timeout=30)

    @property
    def shards(self):
        return self.sharder.shards

    @property
    def user(self):
        return self.sharder.user

    async def fetch_gateway(self):
        data = await rest.get_gateway.request(session=self.manager.rest)
        return data

    async def connect(self, *args, **kwargs):
        gateway = await self.fetch_gateway()

        shard = await self.sharder.create_connection(
            0, gateway['url'], intents=None,
            token=self.manager.token)

        self.shards[0] = shard

        await self.sharder.work()

    def run_forever(self):
        self.manager.loop.create_task(self.connect())
        self.manager.run_forever()
