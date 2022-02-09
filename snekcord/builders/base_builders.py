from __future__ import annotations

import types
import typing
import warnings

import attr

from ..json import JSONObject

if typing.TYPE_CHECKING:
    from typing_extensions import Concatenate, Self

    P = typing.ParamSpec('P')
    T_contra = typing.TypeVar('T_contra', contravariant=True)

    class SetterFunc(typing.Protocol[T_contra, P]):
        def __call__(self, instance: T_contra, /, *args: P.args, **kwargs: P.kwargs) -> None:
            ...


SelfT = typing.TypeVar('SelfT')
ResultT = typing.TypeVar('ResultT')


def setter(func: SetterFunc[SelfT, P]) -> typing.Callable[Concatenate[SelfT, P], SelfT]:
    def wrapped(instance: SelfT, *args: P.args, **kwargs: P.kwargs) -> SelfT:
        func(instance, *args, **kwargs)
        return instance

    return wrapped


@attr.s(kw_only=True, slots=True)
class BaseBuilder:
    data: JSONObject = attr.ib(init=False, factory=dict)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.data!r}>'


@attr.s(kw_only=True, slots=True)
class AwaitableBuilder(typing.Generic[ResultT], BaseBuilder):
    awaited: bool = attr.ib(init=False, default=False)
    result: typing.Optional[ResultT] = attr.ib(init=False, default=None)

    async def action(self) -> ResultT:
        raise NotImplementedError

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

    def __await__(self) -> typing.Generator[None, None, ResultT]:
        if self.awaited:
            raise RuntimeError(f'cannot reuse {self.__class__.__name__}')

        self.awaited = True

        async def wrapper() -> ResultT:
            self.result = await self.action()
            return self.result

        return wrapper().__await__()

    def __del__(self) -> None:
        if not self.awaited:
            warnings.warn(f'{self.__class__.__name__} was never awaited', RuntimeWarning)
