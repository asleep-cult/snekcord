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
    Protocol,
    TYPE_CHECKING,
    TypeVar,
)

if TYPE_CHECKING:
    from ..clients import Client
    from ..events import BaseEvent
    from ..intents import WebSocketIntents
    from ..json import JSONData
    from ..objects import CachedObject
    from ..websockets import Shard
else:
    BaseEvenet = TypeVar('BaseEvent')
    SerializedObject = TypeVar('CachedObject')

__all__ = (
    'EventState',
    'CachedState',
    'CachedEventState',
    'CachedStateView',
)

SupportsUniqueT = TypeVar('SupportsUniqueT')
UniqueT = TypeVar('UniqueT')
CachedObjectT = TypeVar('CachedObjectT', bound=CachedObject)
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

    async def process(self, event: str, shard: Shard, payload: JSONData) -> BaseEvent:
        raise NotImplementedError

    async def dispatch(self, event: str, shard: Shard, paylaod: JSONData) -> None:
        ret = await self.process(event, shard, paylaod)

        for callback in self._callbacks[event]:
            self.client.loop.create_task(callback(ret))


class CacheProvider(Protocol[UniqueT, ObjectT]):
    def contains(self, key: UniqueT) -> bool:
        """Returns True if `key` specifies an existing relationship."""

    async def iterate(self) -> AsyncIterator[ObjectT]:
        """Returns an iterator of all objects in the cache."""

    async def get(self, key: UniqueT) -> Optional[ObjectT]:
        """Returns the object of the relationship specified by `key` or None."""

    async def set(self, key: UniqueT, object: ObjectT) -> None:
        """Creates a new relationship between `key` and `object`."""

    async def delete(self, key: UniqueT) -> Optional[ObjectT]:
        """Deletes the relationship specified by `key` and returns the object or None."""


class MemoryCache(CacheProvider[UniqueT, ObjectT]):
    def __init__(self) -> None:
        self.map: dict[UniqueT, ObjectT] = {}

    def contains(self, key: UniqueT) -> bool:
        return key in self.map

    async def iterate(self) -> AsyncIterator[ObjectT]:
        for object in self.map.values():
            yield object

    async def get(self, key: UniqueT) -> Optional[ObjectT]:
        return self.map.get(key)

    async def set(self, key: UniqueT, object: ObjectT) -> None:
        self.map[key] = object

    async def delete(self, key: UniqueT) -> Optional[ObjectT]:
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

    def view(self, keys: list[UniqueT]) -> CachedStateView[SupportsUniqueT, UniqueT, ObjectT]:
        return CachedStateView(state=self, keys=keys)


class CachedEventState(
    Generic[SupportsUniqueT, UniqueT, CachedObjectT, ObjectT],
    EventState[SupportsUniqueT, UniqueT],
    CachedState[SupportsUniqueT, UniqueT, ObjectT],
):
    cache: CacheProvider[UniqueT, CachedObjectT]

    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.create_cache()

    def create_cache(self) -> None:
        self.cache = MemoryCache()

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        raise NotImplementedError

    async def __aiter__(self) -> AsyncIterator[ObjectT]:
        async for item in self.cache.iterate():
            yield self.from_cached(item)

    async def get(self, object: SupportsUniqueT) -> Optional[ObjectT]:
        object = await self.cache.get(self.to_unique(object))
        return self.from_cached(object)

    async def delete(self, object: SupportsUniqueT) -> Optional[ObjectT]:
        object = await self.cache.delete(self.to_unique(object))
        return self.from_cached(object)

    def from_cached(self, cached: CachedObjectT) -> ObjectT:
        raise NotImplementedError


class CachedStateView(
    Generic[SupportsUniqueT, UniqueT, ObjectT],
    CachedState[SupportsUniqueT, UniqueT, ObjectT],
):
    def __init__(
        self, *, state: CachedState[SupportsUniqueT, UniqueT, ObjectT], keys: list[UniqueT]
    ) -> None:
        self.state = state
        self.keys = keys

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        return self.state.to_unique(object)

    def __contains__(self, object: SupportsUniqueT) -> bool:
        return self.to_unique(object) in self.keys

    async def __aiter__(self) -> AsyncIterator[ObjectT]:
        for key in self.keys:
            yield await self.state.get(key)

    async def get(self, object: SupportsUniqueT) -> Optional[ObjectT]:
        key = self.to_unique(object)
        if key not in self.keys:
            return await self.state.get(key)
