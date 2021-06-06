from __future__ import annotations

from typing import Any, ClassVar, Dict, Generic, Tuple, Type, TypeVar, Union

__all__ = ('Enum',)


TT = TypeVar('TT', bound=type)

class EnumMeta(type):
    def __new__(
        cls: Type[EnumMeta], name: str, bases: Tuple[type, ...], attrs: Dict[str, Any], *, type: type
    ) -> Type[EnumMeta]:
        attrs['__enum_type__'] = type
        return super().__new__(cls, name, bases, attrs)


class Enum(Generic[TT], metaclass=EnumMeta, type=object):
    __enum_type__: ClassVar[TT]
    __enum_names__: ClassVar[Dict[str, Enum[TT]]]
    __enum_values__: ClassVar[Dict[TT, Enum[TT]]]

    def __init__(self, name: str, value: TT) -> None:
        self.name = name
        self.value = value

    def __init_subclass__(cls) -> None:
        cls.__enum_names__ = {}
        cls.__enum_values__ = {}

        for key, value in cls.__dict__.items():
            if (not key.startswith('_')
                    and isinstance(value, cls.__enum_type__)):
                enum = cls(key, value)
                cls.__enum_names__[key] = enum
                cls.__enum_values__[value] = enum

    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.name}, '
                f'value={self.value!r})')

    def __eq__(self, value: Any) -> bool:
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self.__enum_type__):
            return NotImplemented

        return self.value == value

    def __ne__(self, value: Any) -> bool:
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self.__enum_type__):
            return NotImplemented

        return self.value != value

    @classmethod
    def get_enum(cls, value: TT) -> Enum[TT]:
        try:
            return cls.__enum_values__[value]
        except KeyError:
            return cls('undefined', value)

    @classmethod
    def get_value(cls, enum: Union[TT, Enum[TT]]) -> TT:
        if isinstance(enum, cls):
            return enum.value
        elif isinstance(enum, cls.__enum_type__):
            return enum  # type: ignore
        raise ValueError(
            f'{enum!r} is not a valid {cls.__name__}')
