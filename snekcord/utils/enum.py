from __future__ import annotations


import typing as t

from ..typing import Generic

__all__ = ('Enum',)

T = t.TypeVar('T')


class Enum(Generic[T]):
    __enum_names__: t.ClassVar[dict[str, Enum[T]]]
    __enum_values__: t.ClassVar[dict[T, Enum[T]]]
    name: str
    value: T

    def __init__(self, name: str, value: T) -> None:
        self.name = name
        self.value = value

    def __init_subclass__(cls) -> None:
        cls.__enum_names__ = {}
        cls.__enum_values__ = {}

        for key, value in cls.__dict__.items():
            if (not key.startswith('_')
                    and isinstance(value, cls.__generic_type__)):
                enum = cls(key, value)
                cls.__enum_names__[key] = enum
                cls.__enum_values__[value] = enum

    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.name}, '
                f'value={self.value!r})')

    def __eq__(self, value: T | Enum[T]) -> bool:  # type: ignore
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self.__generic_type__):
            return NotImplemented

        return self.value == value

    def __ne__(self, value: T | Enum[T]) -> bool:  # type: ignore
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self.__generic_type__):
            return NotImplemented

        return self.value != value

    @classmethod
    def get_enum(cls, value: T) -> Enum[T]:
        try:
            return cls.__enum_values__[value]
        except KeyError:
            return cls('undefined', value)

    @classmethod
    def get_value(cls, enum: T | Enum[T]) -> T:
        if isinstance(enum, cls):
            return enum.value
        elif isinstance(enum, cls.__generic_type__):
            return enum
        raise ValueError(
            f'{enum!r} is not a valid {cls.__name__}')
