from __future__ import annotations

import asyncio
import typing
from signal import Signals

import asygpy

from loguru import logger

from .client import Client
from ..auth import Authorization
from ..intents import WebSocketIntents
from ..rest.endpoints import (
    GET_GATEWAY,
    GET_GATEWAY_BOT,
)
from ..states import EventState
from ..websockets.shard_websocket import Shard, ShardCancellationToken

if typing.TYPE_CHECKING:
    from ..json import JSONObject

__all__ = ('WebSocketClient',)


class WebSocketClient(Client):
    def __init__(
        self,
        authorization: typing.Union[Authorization, str],
        *,
        intents: WebSocketIntents,
        shard_ids: typing.Optional[typing.Iterable[int]] = None,
    ) -> None:
        super().__init__(authorization)

        if not self.authorization.ws_connectable():
            raise TypeError(f'Cannot connect to gateway using {self.authorization.type.name} token')

        self.shard_ids = tuple(shard_ids) if shard_ids is not None else None
        self.intents = intents

        self._shards: typing.Dict[int, Shard] = {}

    def get_event(self, event: str) -> typing.Optional[EventState]:
        return self.events.get(event)

    def get_shard(self, shard_id: int) -> Shard:
        if self.shard_ids is None:
            raise RuntimeError('cannot get shard before connecting')

        if shard_id not in self.shard_ids:
            raise ValueError(f'Invalid shard id: {shard_id!r}')

        return self._shards[shard_id]

    def get_shards(self) -> typing.Tuple[Shard, ...]:
        return tuple(self._shards.values())

    async def fetch_gateway(self) -> JSONObject:
        if self.authorization.is_bot():
            endpoint = GET_GATEWAY_BOT
        else:
            endpoint = GET_GATEWAY

        return await self.rest.request_api(endpoint)

    async def connect(self) -> typing.Literal[Signals.SIGINT, Signals.SIGTERM]:
        self.loop = asyncio.get_running_loop()

        notifier = asygpy.create_notifier()

        channel = notifier.open_channel()
        channel.add_signal(Signals.SIGINT)
        channel.add_signal(Signals.SIGTERM)

        notifier.start_notifying()

        gateway = await self.fetch_gateway()

        if self.shard_ids is not None:
            sharded = True
        else:
            shards = gateway.get('shards', 1)
            sharded = shards > 1
            self.shard_ids = tuple(range(shards))

        for shard_id in self.shard_ids:
            shard = Shard(self, gateway['url'], shard_id, sharded=sharded)
            self._shards[shard_id] = shard

        for shard in self.get_shards():
            shard.start()

        signum = await channel.receive()
        assert signum in (Signals.SIGINT, Signals.SIGTERM)
        logger.debug(f'Client received signal {signum!r}, shutting down')

        await self.cleanup()

        notifier.stop_notifying()
        return signum

    async def cleanup(self) -> None:
        for shard in self.get_shards():
            await shard.cancel(ShardCancellationToken.SIGNAL_INTERRUPT)

        await asyncio.gather(*(shard.join() for shard in self.get_shards()))
        await self.rest.close()
