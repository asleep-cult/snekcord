from __future__ import annotations

import asyncio
import typing as t

if t.TYPE_CHECKING:
    from typing_extensions import ParamSpec
else:
    class ParamSpec:
        __origin__ = 'typing.ParamSpec'

        args = 'args'
        kwargs = 'kwargs'

        def __init__(self, *args):
            self.__args__ = args


class SupportsTrunc(t.Protocol):
    def __trunc__(self) -> int:
        ...


AnyCallable = t.Callable[..., t.Any]
Json = dict[str, t.Any]
IntConvertable = t.Union[str, bytes, t.SupportsInt, t.SupportsIndex,
                         SupportsTrunc]

T = t.TypeVar('T')
T_contra = t.TypeVar('T_contra', contravariant=True)
P = ParamSpec('P')

Coroutine = t.Coroutine[t.Optional[asyncio.Future[t.Any]], None, T]
CoroCallable = t.Callable[P, Coroutine[T]]
AnyCoroCallable = t.Callable[..., Coroutine[t.Any]]


class Generic(t.Generic[T]):
    __generic_type__: t.ClassVar[type[T]]

    def __class_getitem__(cls, item: type[T]):
        if t.TYPE_CHECKING or isinstance(item, t.TypeVar):
            return cls
        return type(cls.__name__, (cls,),
                    {'__generic_type__': item})
