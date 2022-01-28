from __future__ import annotations

import typing
from types import NoneType

from ..exceptions import IncompleteDataError
from ..undefined import (
    UndefinedType,
    undefined,
)

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from ..json import JSONObject

__all__ = ('CachedModel',)


class ModelField:
    def __init__(self, name: str, type: typing.Any) -> None:
        self.name = name
        self.nullable = NoneType in typing.get_args(type)
        self.optional = UndefinedType in typing.get_args(type)

    def __get__(self, instance: typing.Optional[CachedModel], cls: type[CachedModel]) -> typing.Any:
        if self.name not in instance.__model_data__:
            if not self.optional:
                raise AttributeError(f'{cls.__name__!r} object has no attribute {self.name!r}')

        return instance.__model_data__.get(self.name, undefined)

    def __repr__(self) -> str:
        return f'ModelField(name={self.name}, nullable={self.nullable}, optional={self.optional!r})'


class CachedModel:
    __slots__ = ('__model_data__',)

    __model_fields__: typing.ClassVar[dict[str, ModelField]]
    __model_data__: dict[str, typing.Any]

    def __init_subclass__(cls) -> None:
        cls.__model_fields__ = {}

        annotations = typing.get_type_hints(cls)
        for name, type in annotations.items():
            cls.__model_fields__[name] = ModelField(name, type)

        cls.__dict__.update(cls.__model_fields__)

    def get_fields(self) -> dict[str, ModelField]:
        return self.__model_fields__

    def update(self, data: JSONObject, *, partial: bool = False) -> None:
        for name, field in self.__model_fields__.items():
            if name in data:
                self.__model_data__[name] = data[name]
            else:
                if name in self.__model_data__:
                    continue

                if field.nullable:
                    self.__model_data__[name] = None
                elif not partial and not field.optional:
                    raise IncompleteDataError(self)

    def to_json(self) -> JSONObject:
        return self.__model_data__.copy()

    @classmethod
    def from_json(cls, data: JSONObject, **kwargs: typing.Any) -> Self:
        self = cls.__new__(cls)
        self.update(data)
        cls.__init__(self, **kwargs)
        return self
