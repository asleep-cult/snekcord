from __future__ import annotations

import asyncio
import signal
import socket
import typing

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

    def get_event(self, event: str) -> typing.Optional[EventState[typing.Any, typing.Any]]:
        return self.events.get(event)

    def get_shard(self, shard_id: int) -> Shard:
        if self.shard_ids is None:
            raise RuntimeError('cannot get shard before connecting')

        if shard_id not in self.shard_ids:
            raise ValueError(f'Invalid shard id: {shard_id!r}')

        return self._shards[shard_id]

    def get_shards(self) -> list[Shard]:
        return list(self._shards.values())

    async def fetch_gateway(self) -> JSONObject:
        if self.authorization.is_bot():
            endpoint = GET_GATEWAY_BOT
        else:
            endpoint = GET_GATEWAY

        return await self.rest.request(endpoint)

    async def connect(self) -> None:
        self.loop = asyncio.get_running_loop()

        gateway = await self.fetch_gateway()

        if self.shard_ids is None:
            shards = gateway.get('shards', 1)
            sharded = shards > 1

            self.shard_ids = list(range(shards))
        else:
            sharded = True

        for shard_id in self.shard_ids:
            shard = Shard(self, gateway['url'], shard_id, sharded=sharded)
            self._shards[shard_id] = shard

            shard.start()

        future = self.loop.create_future()

        def set_future_result():
            future.set_result(None)

        async def wait_for_interrupt():
            await future
            logger.debug('Client received signal to shutdown')

        try:
            self.loop.add_signal_handler(signal.SIGINT, set_future_result)
            self.loop.add_signal_handler(signal.SIGTERM, set_future_result)
        except NotImplementedError:
            signal.signal(signal.SIGINT, lambda signum, frame: None)
            signal.signal(signal.SIGTERM, lambda signum, frame: None)

            ssock, csock = socket.socketpair()
            signal.set_wakeup_fd(ssock.fileno())

            def signal_handler(task: asyncio.Task[bytes]) -> None:
                signums = set(task.result())
                if signums.intersection((signal.SIGINT, signal.SIGTERM)):
                    set_future_result()
                else:
                    signal_reader()

            def signal_reader() -> None:
                task = self.loop.create_task(self.loop.sock_recv(csock, 4096))
                task.add_done_callback(signal_handler)

            signal_reader()

        await wait_for_interrupt()

        try:
            self.loop.remove_signal_handler(signal.SIGINT)
            self.loop.remove_signal_handler(signal.SIGTERM)
        except NotImplementedError:
            signal.set_wakeup_fd(-1)

            signal.signal(signal.SIGINT, signal.default_int_handler)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)

        await self.cleanup()

    async def cleanup(self) -> None:
        for shard in self.get_shards():
            await shard.cancel(ShardCancellationToken.SIGNAL_INTERRUPT)

        await asyncio.gather(*(shard.join() for shard in self.get_shards()))
        await self.rest.aclose()
