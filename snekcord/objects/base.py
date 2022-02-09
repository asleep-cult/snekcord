from __future__ import annotations

import typing

import attr

from ..exceptions import UnknownCodeError, UnknownSnowflakeError
from ..snowflake import Snowflake

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from ..clients import Client
    from ..states import CachedState

__all__ = (
    'BaseObject',
    'SnowflakeObject',
    'CodeObject',
    'SnowflakeWrapper',
    'CodeWrapper',
)

SupportsUniqueT = typing.TypeVar('SupportsUniqueT')
UniqueT = typing.TypeVar('UniqueT')
ObjectT = typing.TypeVar('ObjectT')


@attr.s(kw_only=True, slots=True)
class BaseObject(typing.Generic[SupportsUniqueT, UniqueT]):
    """The base class for all Discord objects."""

    state: CachedState[SupportsUniqueT, UniqueT, Self] = attr.ib(repr=False, eq=False, hash=False)

    @property
    def client(self) -> Client:
        return self.state.client


@attr.s(kw_only=True, slots=True, eq=True, hash=True)
class SnowflakeObject(BaseObject[SupportsUniqueT, Snowflake]):
    """The base class for all objects with an id."""

    id: Snowflake = attr.ib(repr=True, eq=True, hash=True)


@attr.s(kw_only=True, slots=True, eq=True, hash=True)
class CodeObject(BaseObject[SupportsUniqueT, str]):
    """The base class for all objects with a code."""

    code: str = attr.field(repr=True, eq=True, hash=True)


class SnowflakeWrapper(typing.Generic[SupportsUniqueT, ObjectT]):
    """A wrapper for a Snowflake allowing for retrieval of the underlying object."""

    def __init__(
        self,
        id: typing.Optional[SupportsUniqueT],
        *,
        state: CachedState[SupportsUniqueT, Snowflake, ObjectT],
    ) -> None:
        self.state = state
        self.id = self.state.to_unique(id) if id is not None else None

    def __repr__(self) -> str:
        return f'SnowflakeWrapper(id={self.id})'

    def unwrap_id(self) -> Snowflake:
        if self.id is None:
            raise TypeError('unwrap_id() called on null wrapper')

        return self.id

    async def unwrap(self) -> ObjectT:
        """Attempts to retrieve the object from cache.

        Example
        -------
        .. code-block:: python

            >>> user = SnowflakeWrapper(506618674921340958, state=client.users)
            >>> await user.unwrap()
            User(id=506618674921340958, name='ToxicKidz', discriminator='4376')

        Raises
        ------
        TypeError
            The wrapper is empty; i.e. the ID is None.
        UnknownSnowflakeError
            The object is not in cache or it does not exist.
        """
        id = self.unwrap_id()

        object = await self.state.get(id)
        if object is None:
            raise UnknownSnowflakeError(id)

        return object


class CodeWrapper(typing.Generic[SupportsUniqueT, ObjectT]):
    """A wrapper for a code allowing for retrieval of the underlying object."""

    def __init__(
        self,
        code: typing.Optional[SupportsUniqueT],
        *,
        state: CachedState[SupportsUniqueT, str, ObjectT],
    ) -> None:
        self.state = state
        self.code = self.state.to_unique(code) if code is not None else None

    def __repr__(self) -> str:
        return f'CodeWrapper(code={self.code!r})'

    def unwrap_code(self) -> str:
        if self.code is None:
            raise TypeError('unwrap() called on empty wrapper')

        return self.code

    async def unwrap(self) -> ObjectT:
        """Attempts to retrieve the object from cache.

        Example
        -------
        .. code-block:: python

            >>> invite = CodeWrapper('kAe2m4hdZ7', state=client.invites)
            >>> await invite.unwrap()
            Invite(code='kAe2m4hdZ7', uses=28)

        Raises
        ------
        TypeError
            The wrapper is empty; i.e. the code is None.
        UnknownCodeError
            The object is not in cache or it does not exist.
        """
        code = self.unwrap_code()

        object = await self.state.get(code)
        if object is None:
            raise UnknownCodeError(code)

        return object
