from __future__ import annotations

import asyncio
import typing
import weakref
from collections import defaultdict

from ..cache import CacheDriver, MemoryCacheDriver
from ..enums import CacheFlags

if typing.TYPE_CHECKING:
    from ..cache import CachedModel
    from ..clients import Client
    from ..events import BaseEvent
    from ..json import JSONObject
    from ..websockets import Shard
else:
    BaseEvent = typing.NewType('BaseEvent', typing.Any)
    CachedModel = typing.NewType('CachedModel', typing.Any)

__all__ = (
    'EventState',
    'CachedState',
    'CachedEventState',
)

SupportsUniqueT = typing.TypeVar('SupportsUniqueT')
UniqueT = typing.TypeVar('UniqueT')
CachedModelT = typing.TypeVar('CachedModelT', bound=CachedModel)
ObjectT = typing.TypeVar('ObjectT')

EventT = typing.TypeVar('EventT', bound=BaseEvent)
OnCallbackT = typing.Callable[[EventT], typing.Coroutine[typing.Any, typing.Any, None]]
OnDecoratorT = typing.Callable[[OnCallbackT[EventT]], OnCallbackT[EventT]]


class EventState:
    """The base class for all states that can receive events."""

    callbacks: defaultdict[str, typing.List[OnCallbackT[typing.Any]]]

    def __init__(self, *, client: Client) -> None:
        self.client = client
        self.callbacks = defaultdict(list)

        for event in self.events:
            self.client.events[event] = self

    @property
    def events(self) -> typing.Tuple[str, ...]:
        """Returns a list of event names that the state can receive."""
        return tuple()

    def on(self, event: str) -> OnDecoratorT[EventT]:
        """A decorator the registers the function to be called when the event is received.

        Raises
        ------
        TypeError
            The specified event is not valid.
        """
        if event not in self.events:
            raise TypeError(f'Invalid event: {event!r}')

        def decorator(callback: OnCallbackT[EventT]) -> OnCallbackT[EventT]:
            if not asyncio.iscoroutinefunction(callback):
                raise TypeError('The callback should be a coroutine function')

            self.callbacks[event].append(callback)
            return callback

        return decorator

    async def create_event(self, event: str, shard: Shard, payload: JSONObject) -> BaseEvent:
        raise NotImplementedError

    async def dispatch(self, event: str, shard: Shard, paylaod: JSONObject) -> None:
        ret = await self.create_event(event, shard, paylaod)

        for callback in self.callbacks[event]:
            asyncio.create_task(callback(ret))


class CachedState(typing.Generic[SupportsUniqueT, UniqueT, ObjectT]):
    """The base class for all states with a cache."""

    client: Client

    def to_unique(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> UniqueT:
        """Converts an object into a unique identifier that can be used for cache operations.

        Raises
        ------
        TypeError
            The object is not supported.
        """
        raise NotImplementedError

    def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        raise NotImplementedError

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        """Retrieves an object from the cache."""
        raise NotImplementedError

    async def size(self) -> int:
        """Returns the number of objects in the cache."""
        raise NotImplementedError

    async def all(self) -> typing.List[ObjectT]:
        """Returns a list containing all of the objects in the cache."""
        return [object async for object in self]


class CachedEventState(
    typing.Generic[SupportsUniqueT, UniqueT, CachedModelT, ObjectT],
    EventState,
    CachedState[SupportsUniqueT, UniqueT, ObjectT],
):
    locks: defaultdict[UniqueT, asyncio.Lock]

    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.cache = self.create_driver()
        self.locks = defaultdict(asyncio.Lock, weakref.WeakValueDictionary())

    def create_driver(self) -> CacheDriver[UniqueT, CachedModelT]:
        """Creates the cache driver to be used by the state.
        All states use an in-memory driver by default."""
        return MemoryCacheDriver()

    def synchronize(self, object: SupportsUniqueT) -> asyncio.Lock:
        """A basic synchronization function that aims to prevent race conditions
        within the upsert method."""
        return self.locks[self.to_unique(object)]

    async def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        async for item in self.cache.iterate():
            yield await self.from_cached(item)

    async def size(self) -> int:
        return await self.cache.size()

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        cached = await self.cache.get(self.to_unique(object))
        if cached is None:
            return None

        return await self.from_cached(cached)

    async def drop(
        self, object: typing.Union[UniqueT, SupportsUniqueT]
    ) -> typing.Optional[ObjectT]:
        """Removes an object from the cache and cleans up any references to it.
        The last known version of the object is returned."""
        cached = await self.cache.drop(self.to_unique(object))
        if cached is None:
            return None

        await self.remove_refs(cached)
        return await self.from_cached(cached)

    async def remove_refs(self, object: CachedModelT) -> None:
        """Removes any references to the object from the corresponding ref-stores.
        This is called as part of the drop routine and should not be called
        manually."""

    async def upsert_cached(
        self, data: JSONObject, flags: CacheFlags = CacheFlags.ALL
    ) -> CachedModelT:
        """Adds or otherwise updates an object in the cache with the data. The provided flags
        should be passed down to other upsert functions, determining which objects should
        be added to the cache."""
        raise NotImplementedError

    async def from_cached(self, cached: CachedModelT) -> ObjectT:
        """Creates an immutable user facing object from a cached model."""
        raise NotImplementedError

    async def upsert(self, data: JSONObject, flags: CacheFlags = CacheFlags.ALL) -> ObjectT:
        """A convencience wrapper for upsert_cached that creates
        a user facing object from the result."""
        cached = await self.upsert_cached(data, flags)
        return await self.from_cached(cached)


class CachedStateView(CachedState[SupportsUniqueT, UniqueT, ObjectT]):
    """A frozen view into a cached state with only a subset of objects."""

    def __init__(
        self,
        *,
        state: CachedState[SupportsUniqueT, UniqueT, ObjectT],
        keys: typing.Iterable[SupportsUniqueT],
    ) -> None:
        self.state = state
        self.client = self.state.client
        self.keys = frozenset(self.to_unique(key) for key in keys)

    def to_unique(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> UniqueT:
        return self.state.to_unique(object)

    def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        iterator = (await self.state.get(key) for key in self.keys)
        return (object async for object in iterator if object is not None)

    async def size(self) -> int:
        return len(self.keys)

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        key = self.to_unique(object)
        if key not in self.keys:
            return None

        return await self.state.get(key)
