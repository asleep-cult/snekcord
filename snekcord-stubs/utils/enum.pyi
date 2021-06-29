from __future__ import annotations

import typing as t

__all__ = ('Enum',)

T = t.TypeVar('T')


class Enum(t.Generic[T]):
    __enum_type__: type[T]
    __enum_names__: t.ClassVar[dict[str, Enum[T]]]
    __enum_values__: t.ClassVar[dict[T, Enum[T]]]

    name: str
    value: T

    def __init__(self, name: str, value: T) -> None: ...

    def __eq__(self, other: T | Enum[T]) -> bool: ...

    def __ne__(self, other: T | Enum[T]) -> bool: ...

    @classmethod
    def get_enum(cls, value: T) -> Enum[T]: ...

    @classmethod
    def get_value(cls, enum: T | Enum[T]) -> T: ...
