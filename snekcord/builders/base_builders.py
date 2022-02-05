from __future__ import annotations

import types
import typing
import warnings

from ..json import JSONObject

if typing.TYPE_CHECKING:
    from typing_extensions import Concatenate, Self

    P = typing.ParamSpec('P')
    T_contra = typing.TypeVar('T_contra', contravariant=True)

    class SetterFunc(typing.Protocol[P, T_contra]):
        def __call__(self, instance: T_contra, /, *args: P.args, **kwargs: P.kwargs) -> None:
            ...


SelfT = typing.TypeVar('SelfT')
ActionT = typing.TypeVar('ActionT')


def setter(func: SetterFunc[P, SelfT]) -> typing.Callable[Concatenate[SelfT, P], SelfT]:
    def wrapped(instance: SelfT, *args: P.args, **kwargs: P.kwargs) -> SelfT:
        func(instance, *args, **kwargs)
        return instance

    return wrapped


class BaseBuilder:
    __slots__ = ('data',)

    def __init__(self) -> None:
        self.data: JSONObject = {}

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.data!r}>'


class AwaitableBuilder(typing.Generic[ActionT], BaseBuilder):
    __slots__ = ('awaited',)

    def __init__(self) -> None:
        super().__init__()
        self.awaited = False

    async def action(self) -> ActionT:
        raise NotImplementedError

    async def __aenter__(self) -> Self:
        if self.awaited:
            raise RuntimeError(f'cannot reuse {self.__class__.__name__}')

        self.awaited = True
        return self

    async def __aexit__(
        self,
        exc_type: typing.Type[BaseException],
        exc_val: BaseException,
        exc_tb: types.TracebackType,
    ) -> None:
        await self.action()

    def __await__(self) -> typing.Generator[None, None, ActionT]:
        if self.awaited:
            raise RuntimeError(f'cannot reuse {self.__class__.__name__}')

        self.awaited = True
        return self.action().__await__()

    def __del__(self) -> None:
        if not self.awaited:
            warnings.warn(f'{self.__class__.__name__} was never awaited', ResourceWarning)
