from __future__ import annotations

import types
import typing
import warnings

import attr

from ..undefined import undefined

if typing.TYPE_CHECKING:
    from typing_extensions import Concatenate, Self

    P = typing.ParamSpec('P')
    T_co = typing.TypeVar('T_co', covariant=True)
    T_contra = typing.TypeVar('T_contra', contravariant=True)

    SelfT = typing.TypeVar('SelfT')
    ResultT = typing.TypeVar('ResultT')

    class SetterFunc(typing.Protocol[T_contra, P]):
        def __call__(self, instance: T_contra, /, *args: P.args, **kwargs: P.kwargs) -> None:
            ...

    class ActionBuilder(typing.Protocol[T_co]):
        awaited: bool
        result: typing.Optional[T_co]

        async def action(self) -> T_co:
            ...


def setter(func: SetterFunc[SelfT, P]) -> typing.Callable[Concatenate[SelfT, P], SelfT]:
    """A decorator that causes a function to return the first argument passed to it.
    This is intended for use by setter methods which return the instance of the
    builder to allow for call chaining."""

    def __setter__(instance: SelfT, *args: P.args, **kwargs: P.kwargs) -> SelfT:
        func(instance, *args, **kwargs)
        return instance

    return __setter__


@attr.s(kw_only=True)
class BaseBuilder:
    def setters(self, **kwargs: typing.Any) -> Self:
        """Calls each setter in **kwargs ignoring undefined values.

        Raises
        ------
        TypeError
            The specified key is not a valid setter.
        """
        for key, value in kwargs.items():
            setter = getattr(self.__class__, key, None)

            if not isinstance(setter, types.FunctionType) or setter.__name__ != '__setter__':
                raise TypeError(f'{key!r} is not a valid setter')

            if value is not undefined:
                setter(self, value)

        return self


@attr.s(kw_only=True)
class AwaitableBuilder(BaseBuilder):
    """The base class for a builder that can be awaited or used in an asnyc with block.
    Instances can only be used once and will emit a resource warning if they are left unused."""

    awaited: bool = attr.ib(init=False, default=False)
    """Whether or not the builder has been awaited or used in an async with block."""

    result: typing.Any = attr.ib(init=False, default=None)
    """The return value of action or None if it hasn't been called yet."""

    async def __aenter__(self) -> Self:
        if self.awaited:
            raise RuntimeError(f'cannot reuse {self.__class__.__name__}')

        self.awaited = True
        return self

    async def __aexit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> None:
        if exc_tb is None:
            self.result = await self.action()

    def __await__(self: ActionBuilder[ResultT]) -> typing.Iterable[ResultT]:
        if self.awaited:
            raise RuntimeError(f'cannot reuse {self.__class__.__name__}')

        async def wrapper() -> ResultT:
            self.result = await self.action()
            return self.result

        self.awaited = True
        return wrapper().__await__()

    async def action(self: ActionBuilder[ResultT]) -> ResultT:
        """Called after the builder is awaited or used in an async with block.
        This method must be implemented in subclasses."""
        raise NotImplementedError

    def __del__(self) -> None:
        if not self.awaited:
            warnings.warn(f'{self.__class__.__name__} was never awaited', RuntimeWarning)
