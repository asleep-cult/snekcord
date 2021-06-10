from __future__ import annotations

import typing as t

__all__ = ('Flag', 'Bitset')

BT = t.TypeVar('BT', bound='Bitset')


class Flag:
    position: int

    def __init__(self, position: int) -> None:
        self.position = position

    @t.overload
    def __get__(self, instance: None, owner: type[Bitset]) -> Flag:
        ...

    @t.overload
    def __get__(self, instance: Bitset, owner: type[Bitset]) -> bool:
        ...

    def __get__(self, instance: Bitset | None,
                owner: type[Bitset]) -> Flag | bool:
        if instance is None:
            return self
        return bool((instance.value >> self.position) & 1)

    def __set__(self, instance: Bitset, value: t.Any) -> None:
        if value:
            instance.value |= (1 << self.position)
        else:
            instance.value &= ~(1 << self.position)

    def __delete__(self, instance: Bitset) -> None:
        instance.value &= ~(1 << self.position)


class Bitset:
    __length__: t.ClassVar[int]
    __bitset_flags__: t.ClassVar[dict[str, Flag]]

    def __init__(self, **kwargs: bool):
        self.value = 0
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls):
        cls.__length__ = 0
        cls.__bitset_flags__ = {}

        for name, value in cls.__dict__.items():
            if isinstance(value, Flag):
                if value.position > cls.__length__:
                    cls.__length__ = value.position
                cls.__bitset_flags__[name] = value

        cls.__length__ += 1

    def __iter__(self) -> t.Generator[bool, None, None]:
        for flag in self.__bitset_flags__:
            yield getattr(self, flag)

    @classmethod
    def all(cls: type[BT]) -> BT:
        return cls.from_value((1 << cls.__length__) - 1)

    @classmethod
    def none(cls: type[BT]) -> BT:
        return cls.from_value(0)

    @classmethod
    def from_value(cls: type[BT], value: int) -> BT:
        self = cls.__new__(cls)
        self.value = value
        return self

    def get_value(self) -> int:
        return self.value

    def to_dict(self) -> dict[str, bool]:
        return dict(zip(self.__bitset_flags__, self))

    def __index__(self) -> int:
        return self.value
