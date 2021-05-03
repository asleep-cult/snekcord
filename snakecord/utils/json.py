from __future__ import annotations

import json
from typing import (
    Any,
    ByteString,
    Callable,
    Dict,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union
)

__all__ = ('JsonTemplate', 'JsonField', 'JsonArray', 'JsonObject')

T = TypeVar('T')


class JsonTemplate(Generic[T]):
    def __init__(self, *,
                 __extends__: Optional[Tuple[JsonTemplate]] = None,
                 **fields: JsonField) -> None:
        self.fields = fields
        if __extends__ is not None:
            for template in __extends__:
                self.fields.update(template.fields)

    @classmethod
    def unmarshal(self, cls: type, data: Union[ByteString, str, dict],
                  *args, **kwargs) -> T:
        if isinstance(data, (bytes, bytearray, memoryview, str)):
            data = json.loads(data)

        o = cls(*args, **kwargs)
        o._update(data, set_default=True)

        return o

    def _update(self, o: T, data: dict, *, set_default: bool = False) -> None:
        for name, field in self.fields.items():
            try:
                setattr(o, name, field.unmarshal(data[field.key]))
            except Exception:
                if set_default:
                    default = None
                    if field.default is not None:
                        default = field.default()
                    setattr(o, name, default)

    def to_dict(self, o: T) -> Dict[str, Any]:
        data = {}

        for name, field in self.fields.items():
            value = getattr(o, name, None)

            if value is None and field.omitempty:
                continue

            try:
                value = field.marshal(value)
            except Exception:
                continue

            if value is None and field.omitempty:
                continue

            data[field.key] = value

        return data

    def marshal(self, o: T) -> str:
        return json.dumps(self.to_dict(o))

    def default_object(self) -> Type[JsonObject]:
        class DefaultObject(JsonObject, template=self):
            pass
        return DefaultObject


class JsonField:
    _unmarshal: Optional[Callable[..., Any]]
    _marshal: Optional[Callable[[Any], Any]]

    def __init__(self, key: str,
                 unmarshal: Optional[Callable[..., Any]] = None,
                 marshal: Optional[Callable[[Any], Any]] = None,
                 object: Optional[Type[JsonObject]] = None,
                 default: Any = None, omitempty: bool = False) -> None:
        self.key = key
        self.object = object
        self.default = default
        self.omitempty = omitempty

        if object is not None:
            self._unmarshal = object.unmarshal
            self._marshal = object.__template__.to_dict
        else:
            self._unmarshal = unmarshal
            self._marshal = marshal

    def unmarshal(self, value: Any) -> Any:
        if self._unmarshal is None:
            return value
        return self._unmarshal(value)

    def marshal(self, value: Any) -> Any:
        if self._marshal is None:
            return value
        return self._marshal(value)


class JsonArray(JsonField):
    def __init__(self, *args, **kwargs) -> None:
        default = kwargs.pop('default', list)
        super().__init__(*args, **kwargs, default=default)

    def unmarshal(self, values: Any) -> Any:
        unmarshalled = []
        for value in values:
            unmarshalled.append(super().unmarshal(value))
        return unmarshalled

    def marshal(self, values: Any) -> Any:
        marshalled = []
        for value in values:
            marshalled.append(super().marshal(value))
        return marshalled


class JsonObjectMeta(type):
    def __new__(mcs: Type[type], name: str,
                bases: tuple[type], attrs: Dict[str, Any],
                template: JsonTemplate) -> JsonObjectMeta:
        slots = set(attrs.pop('__slots__', ()))
        if template is not None:
            slots.update(template.fields)

        attrs['__slots__'] = slots
        attrs['__template__'] = template

        return super().__new__(mcs, name, bases, attrs)


class JsonObject(metaclass=JsonObjectMeta, template=JsonTemplate()):
    __template__: JsonTemplate

    def __new__(cls, *args, **kwargs) -> JsonObject:
        if cls is JsonObject:
            raise TypeError(f'Cannot create instances of {cls.__name__!r}')
        return object.__new__(cls)

    @classmethod
    def unmarshal(cls, *args, **kwargs):
        return cls.__template__.unmarshal(cls, *args, **kwargs)

    def _update(self, *args, **kwargs):
        return self.__template__._update(self, *args, **kwargs)

    def to_dict(self, *args, **kwargs):
        return self.__template__.to_dict(self, *args, **kwargs)

    def marshal(self, *args, **kwargs):
        return self.__template__.marshal(self, *args, **kwargs)
