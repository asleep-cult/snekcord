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


@attr.s(kw_only=True)
class BaseObject(typing.Generic[SupportsUniqueT, UniqueT]):
    """The base class for all Discord objects."""

    state: CachedState[SupportsUniqueT, UniqueT, Self] = attr.ib()

    @property
    def client(self) -> Client:
        return self.state.client


@attr.s(hash=True, kw_only=True)
class SnowflakeObject(BaseObject[SupportsUniqueT, Snowflake]):
    """The base class for all objects with an id."""

    id: Snowflake = attr.field(hash=True, repr=True)


@attr.s(hash=True, kw_only=True)
class CodeObject(BaseObject[SupportsUniqueT, str]):
    """The base class for all objects with a code."""

    code: str = attr.field(hash=True, repr=True)


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
        if self.id is None:
            raise TypeError('unwrap() called on empty wrapper')

        object = await self.state.get(self.id)
        if object is None:
            raise UnknownSnowflakeError(self.id)

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
        if self.code is None:
            raise TypeError('unwrap() called on empty wrapper')

        object = await self.state.get(self.code)
        if object is None:
            raise UnknownCodeError(self.code)

        return object
