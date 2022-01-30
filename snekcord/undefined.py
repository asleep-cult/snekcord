from __future__ import annotations

import enum
import typing

__all__ = ('undefined',)

T = typing.TypeVar('T')


class UndefinedType(enum.Enum):
    undefined = enum.auto()

    def nullify(self, value: MaybeUndefined[T]) -> typing.Optional[T]:
        return value if value is not undefined else None

    def __bool__(self) -> typing.Literal[False]:
        return False


undefined = UndefinedType.undefined
MaybeUndefined = typing.Union[typing.Literal[undefined], T]
