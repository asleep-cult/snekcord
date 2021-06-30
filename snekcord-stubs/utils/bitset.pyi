from __future__ import annotations

import typing as t

__all__ = ('Flag', 'Bitset')

T = t.TypeVar('T')


class Flag:
    position: int

    def __init__(self, position: int) -> None: ...

    @t.overload
    def __get__(self, instance: None, owner: type[Bitset]) -> Flag:
        ...

    @t.overload
    def __get__(self, instance: Bitset, owner: type[Bitset]) -> bool:
        ...


class Bitset:
    _length_: t.ClassVar[int]
    _bitset_flags_: t.ClassVar[dict[str, Flag]]

    def __init__(self, **kwargs: bool) -> None: ...

    def __iter__(self) -> t.Generator[bool, None, None]: ...

    @classmethod
    def all(cls: type[T]) -> T: ...

    @classmethod
    def none(cls: type[T]) -> T: ...

    @classmethod
    def from_value(cls: type[T], value: int) -> T: ...

    def to_dict(self) -> dict[str, bool]: ...
