from .client import Client
from .wsevents import WS_EVENTS
from .. import rest
from ..ws.shardws import Shard

__all__ = ('WebSocketClient',)


class WebSocketClient(Client):
    _events_ = WS_EVENTS

    def __init__(self, *args, **kwargs):
        self.shards = {}
        self.shard_id = kwargs.pop('shard_id', 0)
        self.shard_count = kwargs.pop('shard_count', 1)
        self.intents = kwargs.pop('intents', None)
        self.timeouts = kwargs.pop('timeouts', None)

        super().__init__(*args, **kwargs)

        if not self.authorization.gateway_allowed():
            raise TypeError(f'{self.authorization.type.value} tokens cannot connect to the gateway')

    @property
    def user(self):
        if self.shards:
            return self.shards[self.shard_id].user
        return None

    def fetch_gateway(self):
        return rest.get_gateway.request(self.rest)

    async def connect(self, *args, **kwargs):
        gateway = await self.fetch_gateway()
        gateway_url = gateway['url'] + '?v=9'

        for shard_id in range(self.shard_count):
            shard = Shard(client=self, shard_id=shard_id)
            self.shards[shard_id] = shard

        for shard in self.shards.values():
            await shard.connect(gateway_url, *args, **kwargs)

    def run_forever(self, *args, **kwargs):
        self.loop.create_task(self.connect(*args, **kwargs))
        super().run_forever()
