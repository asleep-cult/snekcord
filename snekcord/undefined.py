import enum
from typing import TypeVar, Union


__all__ = ('undefined',)

T = TypeVar('T')


class UndefinedType(enum.Enum):
    undefined = enum.auto()


undefined = UndefinedType.undefined

MaybeUndefined = Union[undefined, T]
