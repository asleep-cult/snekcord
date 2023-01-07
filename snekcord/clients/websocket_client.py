from __future__ import annotations

import asyncio
import typing
from signal import Signals

import asygpy

from ..api import GatewayAPI, GatewayIntents
from ..auth import Authorization
from .client import Client

if typing.TYPE_CHECKING:
    from ..json import JSONObject
    from ..websockets import Shard

__all__ = ('WebSocketClient',)


class WebSocketClient(Client):
    def __init__(
        self,
        authorization: typing.Union[Authorization, str],
        *,
        intents: GatewayIntents,
        shard_ids: typing.Optional[typing.Iterable[int]] = None,
    ) -> None:
        super().__init__(authorization)

        if not self.authorization.ws_connectable():
            raise TypeError(f'Cannot connect to gateway using {self.authorization.type.name} token')

        self.intents = intents
        self.shard_ids = tuple(shard_ids) if shard_ids is not None else None

        self.gateway_api = self.create_gateway_api()

    def create_gateway_api(self) -> GatewayAPI:
        return GatewayAPI(client=self)

    async def dispatch_event(self, name: str, shard: Shard, data: JSONObject) -> None:
        raise NotImplementedError

    async def connect(self) -> None:
        loop = asyncio.get_running_loop()

        notifier = asygpy.create_notifier()

        channel = notifier.open_channel()
        channel.add_signal(Signals.SIGINT)
        channel.add_signal(Signals.SIGTERM)

        notifier.start_notifying()

        if self.authorization.is_bot():
            gateway = await self.gateway_api.get_gateway_bot()
        else:
            gateway = await self.gateway_api.get_gateway()
