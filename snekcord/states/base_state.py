from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    Generic,
    Iterable,
    Optional,
    TYPE_CHECKING,
    TypeVar,
)

if TYPE_CHECKING:
    from ..clients import Client
    from ..events import BaseEvent
    from ..intents import WebSocketIntents
    from ..json import JSONData
    from ..websockets import Shard
else:
    BaseEvenet = TypeVar('BaseEvent')
    SerializedObject = TypeVar('CachedObject')

__all__ = (
    'EventState',
    'CachedState',
    'CachedEventState',
)

SupportsUniqueT = TypeVar('SupportsUniqueT')
UniqueT = TypeVar('UniqueT')
CachedObjectT = TypeVar('CachedObjectT')
ObjectT = TypeVar('ObjectT')

EventT = TypeVar('EventT', bound=BaseEvent)
OnCallbackT = Callable[[EventT], Awaitable[None]]
OnDecoratorT = Callable[[OnCallbackT[EventT]], OnCallbackT[EventT]]


class EventState(Generic[SupportsUniqueT, UniqueT]):
    def __init__(self, *, client: Client) -> None:
        self.client = client

        self._callbacks = defaultdict(list)
        self._waiters = defaultdict(list)

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        raise NotImplementedError

    def get_events(self) -> Iterable[str]:
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

    async def create_event(self, event: str, shard: Shard, payload: JSONData) -> BaseEvent:
        raise NotImplementedError

    async def dispatch(self, event: str, shard: Shard, paylaod: JSONData) -> None:
        ret = await self.create_event(event, shard, paylaod)

        for callback in self._callbacks[event]:
            self.client.loop.create_task(callback(ret))


class BaseCache(Generic[UniqueT, CachedObjectT]):
    def contains(self, key: UniqueT) -> bool:
        raise NotImplementedError

    async def iterate(self) -> AsyncIterator[CachedObjectT]:
        raise NotImplementedError

    async def get(self, key: UniqueT) -> Optional[CachedObjectT]:
        raise NotImplementedError

    async def set(self, key: UniqueT, object: CachedObjectT) -> None:
        raise NotImplementedError

    async def delete(self, key: UniqueT) -> Optional[CachedObjectT]:
        raise NotImplementedError


class MemoryCache(BaseCache[UniqueT, CachedObjectT]):
    def __init__(self) -> None:
        self.map: dict[UniqueT, CachedObjectT] = {}

    async def iterate(self) -> AsyncIterator[CachedObjectT]:
        for object in self.map.values():
            yield object

    async def get(self, key: UniqueT) -> Optional[CachedObjectT]:
        return self.map.get(key)

    async def set(self, key: UniqueT, object: CachedObjectT) -> None:
        self.map[key] = object

    async def delete(self, key: UniqueT) -> Optional[CachedObjectT]:
        return self.map.pop(key, None)


class CachedState(Generic[SupportsUniqueT, UniqueT, ObjectT]):
    client: Client

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        raise NotImplementedError

    def __contains__(self, object: SupportsUniqueT) -> bool:
        raise NotImplementedError

    async def __aiter__(self) -> AsyncIterator[ObjectT]:
        raise NotImplementedError

    async def get(self, object: SupportsUniqueT) -> Optional[ObjectT]:
        raise NotImplementedError


class CachedEventState(
    Generic[SupportsUniqueT, UniqueT, CachedObjectT, ObjectT],
    EventState[SupportsUniqueT, UniqueT],
    CachedState[SupportsUniqueT, UniqueT, ObjectT],
):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.cache = self.create_cache()

    def create_cache(self) -> BaseCache[UniqueT, CachedObjectT]:
        return MemoryCache()

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        raise NotImplementedError

    async def __aiter__(self) -> AsyncIterator[ObjectT]:
        async for item in self.cache.iterate():
            yield self.from_cached(item)

    async def get(self, object: SupportsUniqueT) -> Optional[ObjectT]:
        object = await self.cache.get(self.to_unique(object))

        if object is not None:
            return self.from_cached(object)

    async def delete(self, object: SupportsUniqueT) -> Optional[ObjectT]:
        object = await self.cache.delete(self.to_unique(object))

        if object is not None:
            return self.from_cached(object)

    def from_cached(self, cached: CachedObjectT) -> ObjectT:
        raise NotImplementedError
