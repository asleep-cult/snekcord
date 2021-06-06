from __future__ import annotations

import typing as t


class SupportsTrunc(t.Protocol):
    def __trunc__(self) -> int:
        ...


AnyCallable = t.Callable[..., t.Any]
Json = dict[str, t.Any]
IntConvertable = t.Union[str, bytes, t.SupportsInt, t.SupportsIndex,
                         SupportsTrunc]

T = t.TypeVar('T')


class Generic(t.Generic[T]):
    __generic_type__: t.ClassVar[type[T]]

    def __class_getitem__(cls, item: type[T]):
        if t.TYPE_CHECKING or isinstance(item, t.TypeVar):
            return cls
        return type(cls.__name__, (cls,),
                    {'__generic_type__': item})
