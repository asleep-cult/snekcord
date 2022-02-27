from __future__ import annotations

import types
import typing
import warnings

import attr

from ..json import JSONObject
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from typing_extensions import Concatenate, Self

    P = typing.ParamSpec('P')
    T = typing.TypeVar('T')
    T_contra = typing.TypeVar('T_contra', contravariant=True)

    SelfT = typing.TypeVar('SelfT')
    ResultT = typing.TypeVar('ResultT')

    class SetterFunc(typing.Protocol[T_contra, P]):
        def __call__(self, instance: T_contra, /, *args: P.args, **kwargs: P.kwargs) -> None:
            ...

    class ActionBuilder(typing.Protocol[T]):
        data: JSONObject
        awaited: bool
        result: typing.Optional[T]

        async def action(self) -> T:
            ...


def setter(func: SetterFunc[SelfT, P]) -> typing.Callable[Concatenate[SelfT, P], SelfT]:
    def wrapped(instance: SelfT, *args: P.args, **kwargs: P.kwargs) -> SelfT:
        func(instance, *args, **kwargs)
        return instance

    return wrapped


@attr.s(kw_only=True)
class BaseBuilder:
    data: JSONObject = attr.ib(init=False, factory=dict)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.data!r}>'

    def setters(self, **kwargs: typing.Any) -> Self:
        for key, value in kwargs.items():
            if value is not undefined:
                try:
                    setter = getattr(self.__class__, key)
                except AttributeError:
                    raise TypeError(f'setters() got an unexpected keyword arguemnt {key!r}')

                setter(value)

        return self


@attr.s(kw_only=True)
class AwaitableBuilder(BaseBuilder):
    awaited: bool = attr.ib(init=False, default=False)
    result: typing.Any = attr.ib(init=False, default=None)

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
        raise NotImplementedError

    def __del__(self) -> None:
        if not self.awaited:
            warnings.warn(f'{self.__class__.__name__} was never awaited', RuntimeWarning)
