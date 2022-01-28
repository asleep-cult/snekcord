from __future__ import annotations

import asyncio
import typing
from collections import defaultdict

from ..cache import (
    CacheDriver,
    MemoryCacheDriver,
)

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..events import BaseEvent
    from ..intents import WebSocketIntents
    from ..json import JSONObject
    from ..websockets import Shard
else:
    BaseEvenet = typing.TypeVar('BaseEvent')
    SerializedObject = typing.TypeVar('CachedObject')

__all__ = (
    'EventState',
    'CachedState',
    'CachedEventState',
)

SupportsUniqueT = typing.TypeVar('SupportsUniqueT')
UniqueT = typing.TypeVar('UniqueT')
CachedObjectT = typing.TypeVar('CachedObjectT')
ObjectT = typing.TypeVar('ObjectT')

EventT = typing.TypeVar('EventT', bound=BaseEvent)
OnCallbackT = typing.Callable[[EventT], typing.Awaitable[None]]
OnDecoratorT = typing.Callable[[OnCallbackT[EventT]], OnCallbackT[EventT]]


class EventState(typing.Generic[SupportsUniqueT, UniqueT]):
    def __init__(self, *, client: Client) -> None:
        self.client = client

        self._callbacks = defaultdict(list)
        self._waiters = defaultdict(list)

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        raise NotImplementedError

    def get_events(self) -> typing.Iterable[str]:
        raise NotImplementedError

    def get_intents(self) -> WebSocketIntents:
        raise NotImplementedError

    def listen(self) -> None:
        self.client.enable_events(self)

    def on(self, event: str) -> OnDecoratorT[BaseEvent]:
        if event not in self.get_events():
            raise TypeError(f'Invalid event: {event!r}')

        def decorator(func: OnCallbackT[BaseEvent]) -> OnCallbackT[BaseEvent]:
            if not asyncio.iscoroutinefunction(func):
                raise TypeError('The callback should be a coroutine function')

            self._callbacks[event].append(func)
            return func

        return decorator

    async def create_event(self, event: str, shard: Shard, payload: JSONObject) -> BaseEvent:
        raise NotImplementedError

    async def dispatch(self, event: str, shard: Shard, paylaod: JSONObject) -> None:
        ret = await self.create_event(event, shard, paylaod)

        for callback in self._callbacks[event]:
            self.client.loop.create_task(callback(ret))


class CachedState(typing.Generic[SupportsUniqueT, UniqueT, ObjectT]):
    client: Client

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        raise NotImplementedError

    def __contains__(self, object: SupportsUniqueT) -> bool:
        raise NotImplementedError

    async def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        raise NotImplementedError

    async def get(self, object: SupportsUniqueT) -> typing.Optional[ObjectT]:
        raise NotImplementedError


class CachedEventState(
    typing.Generic[SupportsUniqueT, UniqueT, CachedObjectT, ObjectT],
    EventState[SupportsUniqueT, UniqueT],
    CachedState[SupportsUniqueT, UniqueT, ObjectT],
):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.cache = self.create_driver()

    def create_driver(self) -> CacheDriver[UniqueT, CachedObjectT]:
        return MemoryCacheDriver()

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        raise NotImplementedError

    async def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        async for item in self.cache.iterate():
            yield self.from_cached(item)

    async def get(self, object: SupportsUniqueT) -> typing.Optional[ObjectT]:
        object = await self.cache.get(self.to_unique(object))

        if object is not None:
            return self.from_cached(object)

    async def delete(self, object: SupportsUniqueT) -> typing.Optional[ObjectT]:
        object = await self.cache.delete(self.to_unique(object))

        if object is not None:
            return self.from_cached(object)

    def from_cached(self, cached: CachedObjectT) -> ObjectT:
        raise NotImplementedError
