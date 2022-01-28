from __future__ import annotations

import typing

__all__ = ('CacheDriver', 'DefaultCacheDriver')

UniqueT = typing.TypeVar('UniqueT')
CachedObjectT = typing.TypeVar('CachedObjectT')


class CacheDriver(typing.Generic[UniqueT, CachedObjectT]):
    async def iterate(self) -> typing.AsyncIterator[CachedObjectT]:
        raise NotImplementedError

    async def create(self, key: UniqueT, object: CachedObjectT) -> None:
        raise NotImplementedError

    async def get(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        raise NotImplementedError

    async def update(self, key: UniqueT, object: CachedObjectT) -> None:
        raise NotImplementedError

    async def delete(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        raise NotImplementedError


class DefaultCacheDriver(CacheDriver[UniqueT, CachedObjectT]):
    def __init__(self) -> None:
        self.map: dict[UniqueT, CachedObjectT] = {}

    async def iterate(self) -> typing.AsyncIterator[CachedObjectT]:
        for object in self.map.values():
            yield object

    async def create(self, key: UniqueT, object: CachedObjectT) -> None:
        self.map[key] = object

    async def get(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        return self.map.get(key)

    async def update(self, key: UniqueT, object: CachedObjectT) -> None:
        return None

    async def delete(self, key: UniqueT) -> typing.Optional[CachedObjectT]:
        return self.map.pop(key, None)
