from __future__ import annotations

import typing

__all__ = ('CacheDriver', 'MemoryCacheDriver')

UniqueT = typing.TypeVar('UniqueT')
CachedObjectT = typing.TypeVar('CachedObjectT')


class CacheDriver(typing.Generic[UniqueT, CachedObjectT]):
    """The abstract base class for all cache drivers."""

    async def size(self) -> int:
        """Reutrns the number of objects in the cache."""
        raise NotImplementedError

    def iterate(self) -> typing.AsyncIterator[CachedObjectT]:
        """Returns an async iterator of all objects in the cache."""
        raise NotImplementedError

    async def create(self, key: UniqueT, object: CachedObjectT) -> None:
        """Creates an entry in the cache for the object specified by key."""
        raise NotImplementedError

    async def get(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        """Retrieves the object in the cache specified by key."""
        raise NotImplementedError

    async def update(self, key: UniqueT, object: CachedObjectT) -> None:
        """Updated the object in the cache specified by key."""
        raise NotImplementedError

    async def drop(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        """Removes the object in the cache specified by key and returns it."""
        raise NotImplementedError


class MemoryCacheDriver(CacheDriver[UniqueT, CachedObjectT]):
    """A simple in-memory cache driver using a dictionary."""

    def __init__(self) -> None:
        self.map: dict[UniqueT, CachedObjectT] = {}

    async def size(self) -> int:
        return len(self.map)

    async def iterate(self) -> typing.AsyncIterator[CachedObjectT]:
        for object in self.map.values():
            yield object

    async def create(self, key: UniqueT, object: CachedObjectT) -> None:
        self.map[key] = object

    async def get(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        return self.map.get(key)

    async def update(self, key: UniqueT, object: CachedObjectT) -> None:
        return None  # the object has already been mutated

    async def drop(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        return self.map.pop(key, None)
