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
        self.is_user = kwargs.pop('user', False)
        self.intents = kwargs.pop('intents', None)
        self.timeouts = kwargs.pop('timeouts', {})
        self.ws_version = kwargs.pop('ws_version', '9')
        self.__events__ = kwargs.pop('events', EVENTS).copy()

        super().__init__(*args, **kwargs)

        self.sharder = Sharder(manager=self, timeout=30)

    @property
    def shards(self):
        return self.sharder.shards

    @property
    def user(self):
        return self.sharder.user

    async def fetch_gateway(self):
        data = await rest.get_gateway.request(session=self.rest)
        return data

    async def fetch_gateway_bot(self):
        data = await rest.get_gateway_bot.request(session=self.rest)
        return data

    async def connect(self, *args, **kwargs):
        if self.is_user or True:
            shard_id = 0
            gateway = await self.fetch_gateway()
            gateway_url = gateway['url'] + f'?v={self.ws_version}'

            shard = await self.sharder.create_connection(
                shard_id, gateway_url, intents=self.intents,
                token=self.token, *args, **kwargs)

            self.shards[shard.id] = shard

        await self.sharder.work()

    def run_forever(self, *args, **kwargs):
        self.loop.create_task(self.connect(*args, **kwargs))
        super().run_forever()
