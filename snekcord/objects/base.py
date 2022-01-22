from __future__ import annotations

from typing import Generic, TYPE_CHECKING, TypeVar

import attr

from ..json import JSONObject
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from typing_extensions import Self

    from ..clients import Client
    from ..states import CachedState

__all__ = ('SerializedObject',)

SupportsUniqueT = TypeVar('SupportsUniqueT')
UniqueT = TypeVar('UniqueT')
ObjectT = TypeVar('ObjectT')


class SerializedObject(Generic[SupportsUniqueT, UniqueT, ObjectT], JSONObject):
    def __init__(self, *, state: CachedState[SupportsUniqueT, UniqueT, ObjectT]) -> None:
        self.state = state

    async def commit(self) -> None:
        """Commit the current version of the object to the cache."""


@attr.s(kw_only=True)
class BaseObject(Generic[SupportsUniqueT, UniqueT]):
    """The base class for all Discord objects."""

    state: CachedState[SupportsUniqueT, UniqueT, Self] = attr.field()

    @property
    def client(self) -> Client:
        return self.state.client


@attr.s(hash=True, kw_only=True)
class SnowflakeObject(Generic[SupportsUniqueT], BaseObject[SupportsUniqueT, Snowflake]):
    """The base class for all objects with an id."""

    id: Snowflake = attr.field(hash=True, repr=True)


@attr.s(hash=True, kw_only=True)
class CodeObject(Generic[SupportsUniqueT], BaseObject[SupportsUniqueT, str]):
    """The base class for all objects with a code."""

    code: str = attr.field(hash=True, repr=True)
