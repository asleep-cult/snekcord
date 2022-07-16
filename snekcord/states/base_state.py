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

EventT = typing.TypeVar('EventT', bound=BaseEvent[typing.Any])
OnCallbackT = typing.Callable[[EventT], typing.Coroutine[typing.Any, typing.Any, None]]
OnDecoratorT = typing.Callable[[OnCallbackT[EventT]], OnCallbackT[EventT]]


class EventState:
    """The base class for all states that can receive events."""

    callbacks: defaultdict[str, typing.List[OnCallbackT[typing.Any]]]

    def __init__(self, *, client: Client) -> None:
        self.client = client
        self.callbacks = defaultdict(list)

    @property
    def events(self) -> typing.Tuple[str, ...]:
        """Return a list of event names that the state can receive."""
        return tuple()

    def register_callback(self, event: str, callback: OnCallbackT[EventT]) -> None:
        """Register a function to be called when an event is received.

        Parameters
        ----------
        event: str
            The name of the event to register the callback to.
        callback: typing.Callable[[BaseEvent], typing.Coroutine[typing.Any, typing.Any, None]]
            The coroutine function to call when the event is received.

        Raises
        ------
        ValueError
            Raised when the event does not exist.
        TypeError
            Raised when the callback is not a coroutine function.
        """
        if event not in self.events:
            raise ValueError(f'{event!r} is not a valid event')

        if not asyncio.iscoroutinefunction(callback):
            raise TypeError('The callback should be a coroutine function.')

        callbacks = self.callbacks[event]
        callbacks.append(callback)

    def on(self, event: str) -> OnDecoratorT[EventT]:
        """Return a decorator that registers the function to be called when an event is received.

        Parameters
        ----------
        event: str
            The name of the event to register the callback to.

        Raises
        ------
        ValueError
            Raised when the event does not exist.
        TypeError
            Raised when the callback is not a coroutine function.

        Example
        -------
        ```py
        @client.messages.on(MessageEvents.Create)
        def on_message_create(evt: snekcord.MessageCreateEvent) -> None:
            print(f'A message was created: {evt.message.content!r}')
        ```
        """

        def decorator(callback: OnCallbackT[EventT]) -> OnCallbackT[EventT]:
            self.register_callback(event, callback)
            return callback

        return decorator

    async def dispatch(self, name: str, event: BaseEvent[typing.Any]) -> None:
        for callback in self.callbacks[name]:
            asyncio.create_task(callback(event))


class CachedState(typing.Generic[SupportsUniqueT, UniqueT, ObjectT]):
    """The base class for all states with a cache."""

    client: Client

    def to_unique(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> UniqueT:
        """Convert an object into a unique identifier.

        Parameters
        ----------
        object: typing.Union[UniqueT, SupportsUniqueT]
            The object to convert.

        Returns
        -------
        UniqueT
            A unique identifier that can be used with cache operations.

        Raises
        ------
        TypeError
            Raised when the object does not support conversion.
        """
        raise NotImplementedError

    def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        raise NotImplementedError

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        """Retrieve an object from cache.

        Parameters
        ----------
        object: typing.Union[UniqueT, SupportsUniqueT]
            The object to use for the cache lookup.

        Returns
        -------
        typing.Optional[ObjectT]
            An object from cache that exists under the unique identifier
            or None if it does not exist.

        Raises
        ------
        TypeError
            Raised when the object cannot be converted into a unique identifier.
        """
        raise NotImplementedError

    async def size(self) -> int:
        """Return the number of objects currently in cache."""
        raise NotImplementedError

    async def all(self) -> typing.List[ObjectT]:
        """Return a list of all objects currently in cahe."""
        return [object async for object in self]


class CachedEventState(
    typing.Generic[SupportsUniqueT, UniqueT, CachedModelT, ObjectT],
    EventState,
    CachedState[SupportsUniqueT, UniqueT, ObjectT],
):
    """A cached state with the ability to receive events."""

    locks: defaultdict[UniqueT, asyncio.Lock]

    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.cache = self.create_driver()
        self.locks = defaultdict(asyncio.Lock, weakref.WeakValueDictionary())

    def create_driver(self) -> CacheDriver[UniqueT, CachedModelT]:
        """Create the cache driver to be used by the state.
        This should be overriden in a subclass for custom cache implementations.

        Returns
        -------
        MemoryCacheDriver
            An in-memory cache driver to be used by the state.
        """
        return MemoryCacheDriver()

    def synchronize(self, object: SupportsUniqueT) -> asyncio.Lock:
        """Return a lock for a specific object. This should be used
        by upsert functions to prevent race conditions.

        Raises
        ------
        TypeError
            Raised when the object cannot be converted into a unique identifier.
        """
        return self.locks[self.to_unique(object)]

    async def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        async for item in self.cache.iterate():
            yield await self.from_cached(item)

    async def size(self) -> int:
        """Return the number of object in cache according to the cache driver."""
        return await self.cache.size()

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        """Retrieve an object from the cache driver.

        Parameters
        ----------
        object: typing.Union[UniqueT, SupportsUniqueT]
            The object to use for the cache lookup.

        Returns
        -------
        typing.Optional[ObjectT]
            The user facing version of the cached object or None if it does not exist.

        Raises
        ------
        TypeError
            Raised when the object cannot be converted into a unique identifier.
        """
        cached = await self.cache.get(self.to_unique(object))
        if cached is None:
            return None

        return await self.from_cached(cached)

    async def drop(
        self, object: typing.Union[UniqueT, SupportsUniqueT]
    ) -> typing.Optional[ObjectT]:
        """Remove an object from the cache driver and clean up any references to it.

        Returns
        -------
        typing.Optional[ObjectT]
            The user facing version of the cached object or None if it does not exist.

        Raises
        ------
        TypeError
            Raised when the object cannot be converted into a unique identifier.
        """
        cached = await self.cache.drop(self.to_unique(object))
        if cached is None:
            return None

        await self.remove_refs(cached)
        return await self.from_cached(cached)

    async def upsert(self, data: typing.Any, flags: CacheFlags = CacheFlags.ALL) -> ObjectT:
        """Add or otherwise update an object in cache. If you do not need the result, consider
        using `snekcord.CachedEventState.upsert_cached` instead.

        Parameters
        ----------
        data: JSONObject
            The data to update the object with.
        flags: CacheFlags
            The flags determining which objects to add to cache.
            This should be passed down to other upsert functions.

        Returns
        -------
        CachedModelT
            A user facing version of the object in cache.
        """
        cached = await self.upsert_cached(data, flags)
        return await self.from_cached(cached)

    async def upsert_cached(
        self, data: typing.Any, flags: CacheFlags = CacheFlags.ALL
    ) -> CachedModelT:
        """Add or otherwise update an object in cache.

        Parameters
        ----------
        data: JSONObject
            The data to update the object with.
        flags: CacheFlags
            The flags determining which objects to add to cache.
            This should be passed down to other upsert functions.

        Returns
        -------
        CachedModelT
            A raw model representing the updated object in cache.
        """
        raise NotImplementedError

    async def from_cached(self, cached: CachedModelT) -> ObjectT:
        """Return an immutable user facing object from a cached model."""
        raise NotImplementedError

    async def remove_refs(self, object: CachedModelT) -> None:
        """Remove any references to object from the corresponding ref-stores.
        This is called as part of the drop routine and should not be called
        manually."""


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
        """Convert an object into a unique identifier using the parent state's functionality.

        Parameters
        ----------
        object: typing.Union[UniqueT, SupportsUniqueT]
            The object to convert.

        Returns
        -------
        UniqueT
            A unique identifier that can be used with cache operations.

        Raises
        ------
        TypeError
            Raised when the object does not support conversion.
        """
        return self.state.to_unique(object)

    def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        iterator = (await self.state.get(key) for key in self.keys)
        return (object async for object in iterator if object is not None)

    async def size(self) -> int:
        """Return the number of items known to be in the state when it was created."""
        return len(self.keys)

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        """Retrieve an object from cache using the parent state's functionality.

        Parameters
        ----------
        object: typing.Union[UniqueT, SupportsUniqueT]
            The object to use for the cache lookup, None is automatically returned
            if the object is not in the state's know set of keys.

        Returns
        -------
        typing.Optional[ObjectT]
            An object from cache that exists under the unique identifier
            or None if it does not exist.

        Raises
        ------
        TypeError
            Raised when the object cannot be converted into a unique identifier.
        """
        key = self.to_unique(object)
        if key not in self.keys:
            return None

        return await self.state.get(key)
