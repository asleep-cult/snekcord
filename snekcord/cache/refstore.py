from __future__ import annotations

import array
import contextlib
import typing
from collections import defaultdict

from ..snowflake import Snowflake, SnowflakeIterator

__all__ = ('RefStore', 'MemoryRefStore', 'SnowflakeMemoryRefStore')

UniqueT = typing.TypeVar('UniqueT')
RefT = typing.TypeVar('RefT')


class RefStore(typing.Generic[UniqueT, RefT]):
    async def get(self, key: UniqueT) -> typing.Iterable[RefT]:
        raise NotImplementedError

    async def add(self, key: UniqueT, ref: RefT) -> None:
        raise NotImplementedError

    async def remove(self, key: UniqueT, ref: RefT) -> None:
        raise NotImplementedError

    async def clear(self, key: UniqueT) -> None:
        raise NotImplementedError


class MemoryRefStore(RefStore[UniqueT, RefT]):
    refs: defaultdict[UniqueT, typing.List[RefT]]

    def __init__(self) -> None:
        self.refs = defaultdict(list)

    async def get(self, key: UniqueT) -> typing.Iterable[RefT]:
        return iter(self.refs[key])

    async def add(self, key: UniqueT, ref: RefT) -> None:
        self.refs[key].append(ref)

    async def remove(self, key: UniqueT, ref: RefT) -> None:
        refs = self.refs.get(key)
        if refs is None:
            return None

        with contextlib.suppress(ValueError):
            refs.remove(ref)

    async def clear(self, key: UniqueT) -> None:
        self.refs.pop(key, None)


class SnowflakeMemoryRefStore(RefStore[UniqueT, Snowflake]):
    refs: defaultdict[UniqueT, array.array[int]]

    def __init__(self) -> None:
        self.refs = defaultdict(lambda: array.array('Q'))

    async def get(self, key: UniqueT) -> typing.Iterable[Snowflake]:
        return SnowflakeIterator(self.refs[key])

    async def add(self, key: UniqueT, ref: Snowflake) -> None:
        self.refs[key].append(ref)

    async def remove(self, key: UniqueT, ref: Snowflake) -> None:
        refs = self.refs.get(key)
        if refs is None:
            return None

        with contextlib.suppress(ValueError):
            refs.remove(ref)

    async def clear(self, key: UniqueT) -> None:
        self.refs.pop(key, None)
