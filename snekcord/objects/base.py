from __future__ import annotations

import typing

import attr

from ..exceptions import UnknownCodeError, UnknownSnowflakeError
from ..snowflake import Snowflake

if typing.TYPE_CHECKING:
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
TypeT = typing.TypeVar('TypeT')


@attr.s(kw_only=True, slots=True)
class BaseObject:
    """The base class for all Discord objects."""

    client: Client = attr.ib(repr=False, eq=False)


@attr.s(kw_only=True, slots=True, eq=True, hash=True)
class SnowflakeObject(BaseObject):
    """The base class for all Discord objects with an id."""

    id: Snowflake = attr.ib(repr=True, eq=True, hash=True)


@attr.s(kw_only=True, slots=True, eq=True, hash=True)
class CodeObject(BaseObject):
    """The base class for all Discord objects with a code."""

    code: str = attr.field(repr=True, eq=True, hash=True)


class SnowflakeWrapper(typing.Generic[SupportsUniqueT, ObjectT]):
    """A wrapper for a Snowflake allowing for retrieval of the
    underlying object from its respective cache."""

    def __init__(
        self,
        id: typing.Optional[SupportsUniqueT] = None,
        *,
        state: CachedState[SupportsUniqueT, Snowflake, ObjectT],
    ) -> None:
        self.state = state
        self.id = self.state.to_unique(id) if id is not None else None

    def __repr__(self) -> str:
        return f'SnowflakeWrapper(id={self.id})'

    @property
    def client(self) -> Client:
        return self.state.client

    def unwrap_id(self) -> Snowflake:
        """Return the wrapper's id, raises TypeError if the id is None."""
        if self.id is None:
            raise TypeError('unwrap_id() called on empty wrapper')

        return self.id

    async def unwrap(self) -> ObjectT:
        """Retrieve the object from cache.

        Returns
        -------
        ObjectT
            The object from cache with the same id.

        Raises
        ------
        TypeError
            The wrapper is empty (the id is None.)
        UnknownSnowflakeError
            The object is not in cache or it does not exist.

        Example
        -------
        ```py
        >>> user = SnowflakeWrapper(506618674921340958, state=client.users)
        >>> await user.unwrap()
        User(id=506618674921340958, name='ToxicKidz', discriminator='4376')
        ```
        """
        id = self.unwrap_id()

        object = await self.state.get(id)
        if object is None:
            raise UnknownSnowflakeError(id)

        return object

    async def unwrap_as(self, type: typing.Type[TypeT]) -> TypeT:
        """Unwrap the object and enforce a type check on the return value.
        This is useful for states the can create multiple different types.

        Raises
        ------
        TypeError
            Raised when the unwrapped object does not match the provided type.

        Example
        -------
        ```py
        >>> channel = SnowflakeWrapper(834891949781549056, state=client.channels)
        >>> await channel.unwrap_as(snekcord.TextChannel)
        TextChannel(id=834891949781549056, name='github')
        """
        object = await self.unwrap()

        if not isinstance(object, type):
            raise TypeError(f'Expected {type.__name__!r} for {object.__class__.__name__}')

        return object


class CodeWrapper(typing.Generic[SupportsUniqueT, ObjectT]):
    """A wrapper for a code allowing for retrieval of the
    underlying object from its respective cache."""

    def __init__(
        self,
        code: typing.Optional[SupportsUniqueT] = None,
        *,
        state: CachedState[SupportsUniqueT, str, ObjectT],
    ) -> None:
        self.state = state
        self.code = self.state.to_unique(code) if code is not None else None

    def __repr__(self) -> str:
        return f'CodeWrapper(code={self.code!r})'

    @property
    def client(self) -> Client:
        return self.state.client

    def unwrap_code(self) -> str:
        """Returns the wrapper's code or raises TypeError if the code is None."""
        if self.code is None:
            raise TypeError('unwrap_code() called on empty wrapper')

        return self.code

    async def unwrap(self) -> ObjectT:
        """Retrieve the object from cache.

        Returns
        -------
        ObjectT
            The object from cache with the same code.

        Raises
        ------
        TypeError
            The wrapper is empty (the code is None.)
        UnknownCodeError
            The object is not in cache or it does not exist.

        Example
        -------
        ```py
        >>> invite = CodeWrapper('kAe2m4hdZ7', state=client.invites)
        >>> await invite.unwrap()
        Invite(code='kAe2m4hdZ7', uses=28)
        ```
        """
        code = self.unwrap_code()

        object = await self.state.get(code)
        if object is None:
            raise UnknownCodeError(code)

        return object

    async def unwrap_as(self, type: typing.Type[TypeT]) -> TypeT:
        """Unwrap the object and enforce a type check on the return value.
        This is useful for states the can create multiple different types."""
        object = await self.unwrap()

        if not isinstance(object, type):
            raise TypeError(f'Expected {type.__name__!r} for {object.__class__.__name__}')

        return object
