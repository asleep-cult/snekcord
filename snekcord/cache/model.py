from __future__ import annotations

import typing

from ..exceptions import IncompleteDataError
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from ..json import JSONObject

__all__ = ('CachedModel',)


class ModelField:
    def __init__(self, name: str, annotation: typing.Any) -> None:
        self.name = name
        self.nullable = type(None) in typing.get_args(annotation)
        self.optional = typing.Literal[undefined] in typing.get_args(annotation)

    def __repr__(self) -> str:
        return f'ModelField(name={self.name}, nullable={self.nullable}, optional={self.optional!r})'


class CachedModelMeta(type):
    def __new__(
        cls, name: str, bases: typing.Tuple[type, ...], namespace: typing.Dict[str, typing.Any]
    ) -> type:
        model_fields: typing.Dict[str, ModelField] = {}

        slots: typing.Set[str] = set()
        for annotation in namespace['__annotations__']:
            if not annotation.startswith('__') and not annotation.endswith('__'):
                slots.add(annotation)

        if '__slots__' in namespace:
            slots.update(namespace['__slots__'])

        namespace['__slots__'] = tuple(slots)
        namespace['__model_fields__'] = model_fields

        self = type.__new__(cls, name, bases, namespace)

        annotations = typing.get_type_hints(self)
        for name, annotation in annotations.items():
            if not name.startswith('__') and not name.endswith('__'):
                model_fields[name] = ModelField(name, annotation)

        return self


class CachedModel(metaclass=CachedModelMeta):
    __model_fields__: typing.ClassVar[typing.Dict[str, ModelField]]

    def get_fields(self) -> typing.Dict[str, ModelField]:
        return self.__model_fields__

    def update(self, data: JSONObject, *, partial: bool = False) -> None:
        for name, field in self.__model_fields__.items():
            if name in data:
                setattr(self, name, data[name])

            elif not hasattr(self, name):
                if field.nullable or field.optional:
                    setattr(self, name, undefined if field.optional else None)

                elif not partial:
                    raise IncompleteDataError(self, name)

    def to_json(self) -> JSONObject:
        data: JSONObject = {}

        for name in self.__model_fields__:
            value = getattr(self, name, undefined)
            if value is not undefined:
                data[name] = value

        return data

    @classmethod
    def from_json(cls, data: JSONObject, **kwargs: typing.Any) -> Self:
        self = cls.__new__(cls)
        self.update(data)

        cls.__init__(self, **kwargs)
        return self
