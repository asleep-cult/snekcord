from __future__ import annotations

from typing import Generic, Optional, TYPE_CHECKING, TypeVar

import attr

from ..exceptions import UnknownObjectError
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from ..clients import Client
    from ..states import CachedState

__all__ = (
    'BaseObject',
    'SnowflakeObject',
    'CodeObject',
    'SnowflakeWrapper',
    'CodeWrapper',
)

SupportsUniqueT = TypeVar('SupportsUniqueT')
UniqueT = TypeVar('UniqueT')
ObjectT = TypeVar('ObjectT')

SnowflakeState = CachedState[SupportsUniqueT, Snowflake, ObjectT]
CodeState = CachedState[SupportsUniqueT, str, ObjectT]


@attr.s(kw_only=True)
class BaseObject(Generic[SupportsUniqueT, UniqueT, ObjectT]):
    """The base class for all Discord objects."""

    state: CachedState[SupportsUniqueT, UniqueT, ObjectT] = attr.ib()

    @property
    def client(self) -> Client:
        return self.state.client


@attr.s(hash=True, kw_only=True)
class SnowflakeObject(BaseObject[SupportsUniqueT, Snowflake, ObjectT]):
    """The base class for all objects with an id."""

    id: Snowflake = attr.field(hash=True, repr=True)


@attr.s(hash=True, kw_only=True)
class CodeObject(BaseObject[SupportsUniqueT, str, ObjectT]):
    """The base class for all objects with a code."""

    code: str = attr.field(hash=True, repr=True)


class SnowflakeWrapper(BaseObject[SupportsUniqueT, Snowflake, ObjectT]):
    """A wrapper for a Snowflake allowing for retrieval of the underlying object."""

    def __init__(
        self, id: Optional[SupportsUniqueT], *, state: SnowflakeState[SupportsUniqueT, ObjectT]
    ) -> None:
        super().__init__(state=state)

        if id is not None:
            self.id = self.state.to_unique(id)
        else:
            self.id = None

    async def unwrap(self) -> ObjectT:
        if self.id is None:
            raise UnknownObjectError(None)

        object = await self.state.get(self.id)
        if object is None:
            raise UnknownObjectError(self.id)

        return object


class CodeWrapper(BaseObject[SupportsUniqueT, str, ObjectT]):
    """A wrapper for a code allowing for retrieval of the underlying object."""

    def __init__(
        self, code: Optional[SupportsUniqueT], *, state: CodeState[SupportsUniqueT, ObjectT]
    ) -> None:
        super().__init__(state=state)

        if code is not None:
            self.code = self.state.to_unique(code)
        else:
            self.code = None

    async def unwrap(self) -> ObjectT:
        if self.code is None:
            raise UnknownObjectError(None)

        object = await self.state.get(self.code)
        if object is None:
            raise UnknownObjectError(self.code)

        return object
