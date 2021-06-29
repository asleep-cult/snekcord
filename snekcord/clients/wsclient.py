from .client import Client
from .wsevents import WS_EVENTS
from .. import rest
from ..ws.shardws import Shard

__all__ = ('WebSocketClient',)


class WebSocketClient(Client):
    _events_ = WS_EVENTS

    def __init__(self, *args, user=True, intents=None, timeouts=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_user = user
        self.intents = intents
        self.timeouts = timeouts
        self.shards = {}

    @property
    def user(self):
        if self.shards:
            return next(iter(self.shards.values())).user
        return None

    async def fetch_gateway(self):
        data = await rest.get_gateway.request(session=self.rest)
        return data

    async def fetch_gateway_bot(self):
        data = await rest.get_gateway_bot.request(session=self.rest)
        return data

    async def connect(self, *args, **kwargs):
        if self.is_user or True:
            shard_id = 0
            self.shard_count = 1

            gateway = await self.fetch_gateway()
            gateway_url = gateway['url'] + '?v=9'

            shard = Shard(client=self, shard_id=shard_id)
            await shard.connect(gateway_url, *args, **kwargs)

            self.shards[shard.id] = shard

    def run_forever(self, *args, **kwargs):
        self.loop.create_task(self.connect(*args, **kwargs))
        super().run_forever()
