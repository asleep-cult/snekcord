from __future__ import annotations

import typing as t

__all__ = ('Enum',)

T = t.TypeVar('T')


class Enum(t.Generic[T]):
    _enum_type_: type[T]
    _enum_names_: t.ClassVar[dict[str, Enum[T]]]
    _enum_values_: t.ClassVar[dict[T, Enum[T]]]

    name: str
    value: T

    def __init__(self, name: str, value: T) -> None: ...

    def __eq__(self, other: T | Enum[T]) -> bool: ...

    def __ne__(self, other: T | Enum[T]) -> bool: ...

    @classmethod
    def get_enum(cls, value: T) -> Enum[T]: ...

    @classmethod
    def get_value(cls, enum: T | Enum[T]) -> T: ...
