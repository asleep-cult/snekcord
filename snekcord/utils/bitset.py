from __future__ import annotations

from typing import Any, ClassVar, Dict, Optional, Type, TypeVar, Union, overload

__all__ = ('Bitset', 'Flag', 'NamedBitset')

BT = TypeVar('BT', bound='Bitset')

class Bitset:
    length: int

    def __init__(self, value: int = 0):
        self.value = value

    def _noamalize_indice(self, indice: Any) -> int:
        if not isinstance(indice, int):
            raise TypeError(f'{self.__class__.__name__} indices must be '
                            f'integers, got {indice.__class__.__name__}')

        return indice

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value == other.value

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length != other.length or self.value != other.value

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value > other.value

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value >= other.value

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value < other.value

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value <= other.value

    def __index__(self) -> int:
        return self.value

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, position: int) -> int:
        return (self.value >> self._noamalize_indice(position)) & 1

    def __setitem__(self, position: int, value: int) -> None:
        if value:
            self.value |= (1 << self._noamalize_indice(position))
        else:
            del self[position]

    def __delitem__(self, position: int) -> None:
        self.value &= ~(1 << self._noamalize_indice(position))


class Flag:
    position: int

    def __init__(self, position: int) -> None:
        self.position = position

    @overload
    def __get__(self: Flag, instance: None, owner: Type[Bitset]) -> Flag:
        ...

    @overload
    def __get__(self, instance: BT, owner: Type[BT]) -> int:
        ...

    def __get__(self, instance: Optional[BT], owner: Type[BT]) -> Union[Flag, int]:
        if instance is None:
            return self
        return instance[self.position]

    def __set__(self, instance: Bitset, value: bool) -> None:
        instance[self.position] = value

    def __delete__(self, instance: Bitset) -> None:
        del instance[self.position]


class NamedBitset(Bitset):
    __length__: ClassVar[int]
    __bitset_flags__: ClassVar[Dict[str, Flag]]

    def __init__(self, **kwargs: bool):
        super().__init__()

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

    @classmethod
    def all(cls) -> NamedBitset:
        return cls.from_value((1 << cls.__length__) - 1)

    @classmethod
    def none(cls) -> NamedBitset:
        return cls.from_value(0)

    @classmethod
    def from_value(cls, value: int) -> NamedBitset:
        self = cls.__new__(cls)
        Bitset.__init__(self, int(value))
        return self

    def get_value(self) -> int:
        return self.value

    def to_dict(self) -> Dict[str, NamedBitset]:
        return dict(zip(self.__bitset_flags__, self))  # type: ignore
