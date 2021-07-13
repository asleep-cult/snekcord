import warnings

from .client import Client
from .wsevents import WS_EVENTS, WS_EVENTS_INTENTS
from .. import rest
from ..flags import WebSocketIntents
from ..ws.shardws import Shard

__all__ = ('WebSocketClient',)


class WebSocketClient(Client):
    _events_ = WS_EVENTS

    def __init__(self, *args, **kwargs):
        self.shards = {}
        self.shard_id = kwargs.pop('shard_id', 0)
        self.shard_count = kwargs.pop('shard_count', 1)
        self.timeouts = kwargs.pop('timeouts', None)

        intents = int(kwargs.pop('intents', 0))
        self.intents = WebSocketIntents.from_value(intents)

        self.auto_intents = kwargs.pop('auto_intents', True)

        self.connected = False

        super().__init__(*args, **kwargs)

        if not self.authorization.gateway_allowed():
            raise TypeError(f'{self.authorization.type.value} tokens cannot connect to the gateway')

    @property
    def user(self):
        if self.shards:
            return self.shards[self.shard_id].user
        return None

    def _handle_intent(self, name):
        intent = WS_EVENTS_INTENTS.get(name)

        if intent is not None:
            if self.auto_intents and not self.connected:
                setattr(self.intents, intent, True)
            else:
                warnings.warn(
                    f'The {name!r} event requires the {intent!r} intent to be enabled, '
                    f'this event will not be received from Discord.'
                )

    def register_listener(self, *args, **kwargs):
        listener = super().register_listener(*args, **kwargs)
        self._handle_intent(listener.name)
        return listener

    def register_waiter(self, *args, **kwargs):
        waiter = super().register_waiter(*args, **kwargs)
        self._handle_intent(waiter.name)
        return waiter

    def fetch_gateway(self):
        return rest.get_gateway.request(self.rest)

    async def connect(self, *args, **kwargs):
        gateway = await self.fetch_gateway()
        gateway_url = gateway['url'] + '?v=9'

        for shard_id in range(self.shard_count):
            shard = Shard(shard_id=shard_id, client=self)
            self.shards[shard_id] = shard

        for shard in self.shards.values():
            await shard.ws.connect(gateway_url, *args, **kwargs)

        self.connected = True

    def run_forever(self, *args, **kwargs):
        self.loop.create_task(self.connect(*args, **kwargs))
        super().run_forever()
