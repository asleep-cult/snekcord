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
    """The abstract base class for all ref-stores. Ref-stores can be thought of as
    storage containers for objects who are related to one-another in some way.
    An example of this would be a mapping of guild ids to every channel id in the guild."""

    async def get(self, key: UniqueT) -> typing.Iterable[RefT]:
        """Retrieves the references under key."""
        raise NotImplementedError

    async def add(self, key: UniqueT, ref: RefT) -> None:
        """Adds a reference under key."""
        raise NotImplementedError

    async def remove(self, key: UniqueT, ref: RefT) -> None:
        """Removes a reference under key."""
        raise NotImplementedError

    async def clear(self, key: UniqueT) -> None:
        """Clears every reference under key."""
        raise NotImplementedError


class MemoryRefStore(RefStore[UniqueT, RefT]):
    """A simple in-memory ref-store using a defaultdict of lists."""

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
    """An in-memory ref-store optimized for Snowflakes by using a defaultdict of arrays."""

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
