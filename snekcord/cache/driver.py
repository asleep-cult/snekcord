from __future__ import annotations

import typing

__all__ = ('CacheDriver', 'MemoryCacheDriver')

UniqueT = typing.TypeVar('UniqueT')
CachedObjectT = typing.TypeVar('CachedObjectT')


class CacheDriver(typing.Generic[UniqueT, CachedObjectT]):
    async def len(self) -> int:
        raise NotImplementedError

    def iterate(self) -> typing.AsyncIterator[CachedObjectT]:
        raise NotImplementedError

    async def create(self, key: UniqueT, object: CachedObjectT) -> None:
        raise NotImplementedError

    async def get(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        raise NotImplementedError

    async def update(self, key: UniqueT, object: CachedObjectT) -> None:
        raise NotImplementedError

    async def drop(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        raise NotImplementedError


class MemoryCacheDriver(CacheDriver[UniqueT, CachedObjectT]):
    def __init__(self) -> None:
        self.map: dict[UniqueT, CachedObjectT] = {}

    async def len(self) -> int:
        return len(self.map)

    async def iterate(self) -> typing.AsyncIterator[CachedObjectT]:
        for object in self.map.values():
            yield object

    async def create(self, key: UniqueT, object: CachedObjectT) -> None:
        self.map[key] = object

    async def get(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        return self.map.get(key)

    async def update(self, key: UniqueT, object: CachedObjectT) -> None:
        return None

    async def drop(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        return self.map.pop(key, None)
