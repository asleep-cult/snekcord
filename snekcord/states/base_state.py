from __future__ import annotations

import asyncio
import typing
import weakref
from collections import defaultdict

from ..cache import (
    CacheDriver,
    DefaultCacheDriver,
)

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..cache import CachedModel
    from ..events import BaseEvent
    from ..intents import WebSocketIntents
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
OnCallbackT = typing.Callable[[EventT], typing.Awaitable[None]]
OnDecoratorT = typing.Callable[[OnCallbackT[EventT]], OnCallbackT[EventT]]


class EventState(typing.Generic[SupportsUniqueT, UniqueT]):
    _callbacks: defaultdict[str, list[OnCallbackT[BaseEvent]]]

    def __init__(self, *, client: Client) -> None:
        self.client = client

        self._callbacks = defaultdict(list)

    def to_unique(self, object: SupportsUniqueT) -> UniqueT:
        raise NotImplementedError

    def get_events(self) -> typing.Iterable[str]:
        raise NotImplementedError

    def get_intents(self) -> WebSocketIntents:
        raise NotImplementedError

    def on(self, event: str) -> OnDecoratorT[EventT]:
        # if event not in self.get_events():
        #    raise TypeError(f'Invalid event: {event!r}')

        def decorator(callback: OnCallbackT[EventT]) -> OnCallbackT[EventT]:
            if not asyncio.iscoroutinefunction(callback):
                raise TypeError('The callback should be a coroutine function')

            self._callbacks[event].append(callback)
            return callback

        return decorator

    async def create_event(self, event: str, shard: Shard, payload: JSONObject) -> BaseEvent:
        raise NotImplementedError

    async def dispatch(self, event: str, shard: Shard, paylaod: JSONObject) -> None:
        ret = await self.create_event(event, shard, paylaod)

        for callback in self._callbacks[event]:
            asyncio.create_task(callback(ret))


class CachedState(typing.Generic[SupportsUniqueT, UniqueT, ObjectT]):
    client: Client

    def to_unique(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> UniqueT:
        raise NotImplementedError

    def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        raise NotImplementedError

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        raise NotImplementedError


class CachedEventState(  # type: ignore
    typing.Generic[SupportsUniqueT, UniqueT, CachedModelT, ObjectT],
    EventState[SupportsUniqueT, UniqueT],
    CachedState[SupportsUniqueT, UniqueT, ObjectT],
):
    locks: defaultdict[UniqueT, asyncio.Lock]

    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.cache = self.create_driver()
        self.locks = defaultdict(asyncio.Lock, weakref.WeakValueDictionary())

    def create_driver(self) -> CacheDriver[UniqueT, CachedModelT]:
        return DefaultCacheDriver()

    def to_unique(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> UniqueT:
        raise NotImplementedError

    def synchronize(self, object: SupportsUniqueT) -> asyncio.Lock:
        return self.locks[self.to_unique(object)]

    async def __aiter__(self) -> typing.AsyncIterator[ObjectT]:
        async for item in self.cache.iterate():
            yield await self.from_cached(item)

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        cached = await self.cache.get(self.to_unique(object))
        if cached is not None:
            return await self.from_cached(cached)

    async def delete(
        self, object: typing.Union[UniqueT, SupportsUniqueT]
    ) -> typing.Optional[ObjectT]:
        cached = await self.cache.delete(self.to_unique(object))

        if cached is not None:
            await self.remove_refs(cached)
            return await self.from_cached(cached)

    async def remove_refs(self, object: CachedModelT) -> None:
        return None

    async def from_cached(self, cached: CachedModelT) -> ObjectT:
        raise NotImplementedError


class CachedStateView(CachedState[SupportsUniqueT, UniqueT, ObjectT]):
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

    async def get(self, object: typing.Union[UniqueT, SupportsUniqueT]) -> typing.Optional[ObjectT]:
        key = self.to_unique(object)
        if key in self.keys:
            return await self.state.get(key)
