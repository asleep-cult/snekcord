from __future__ import annotations

import json
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Set, Tuple, Type, TypeVar, Union

__all__ = ('JsonTemplate', 'JsonField', 'JsonArray', 'JsonObject')

T = TypeVar('T')
OT = TypeVar('OT', bound='JsonObject')

class JsonTemplate:
    def __init__(self, *, __extends__: Tuple[JsonTemplate, ...] = (), **fields: JsonField
    ) -> None:
        self.local_fields = fields
        self.fields = self.local_fields.copy()

        for template in __extends__:
            self.fields.update(template.fields)

    def update(self, obj: JsonObject, data: Dict[str, Any], *, set_defaults: bool = False
    ) -> None:
        for name, field in self.fields.items():
            try:
                value = field.unmarshal(data[field.key])
                obj.__fields__.add(field.key)
                setattr(obj, name, value)
            except Exception:
                if set_defaults:
                    default = field.default()
                    if default is not None:
                        obj.__fields__.add(field.key)
                    setattr(obj, name, default)

    def to_dict(self, obj: JsonObject) -> Dict[str, Any]:
        data = {}

        for name, field in self.fields.items():
            if field.key not in obj.__fields__:
                continue

            value = getattr(obj, name, field.default())

            try:
                value = field.marshal(value)
            except Exception:
                continue

            data[field.key] = value

        return data

    def marshal(self, obj: JsonObject, *args: Any, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(obj), *args, **kwargs)

    def default_object(self, name: str = 'GenericObject') -> JsonObjectMeta[JsonObject]:
        return JsonObjectMeta(name, (JsonObject,), {},
                              template=self)


class JsonField:
    def __init__(self, key: str, unmarshal: Optional[Callable[[Any]]] = None,
                marshal: Optional[Callable[[Any]]] = None, object: Optional[JsonObject] = None,
                default: Any = None
        ) -> None:
        self.key = key
        self.object = object
        self._default = default

        if self.object is not None:
            self._unmarshal = self.object.unmarshal
            self._marshal = self.object.__template__.to_dict
        else:
            self._unmarshal = unmarshal
            self._marshal = marshal

    def unmarshal(self, value: Any) -> Any:
        if self._unmarshal is not None:
            value = self._unmarshal(value)
        return value

    def marshal(self, value: Any) -> Any:
        if self._marshal is not None:
            value = self._marshal(value)
        return value

    def default(self) -> Any:
        if callable(self._default):
            return self._default()
        return self._default


class JsonArray(JsonField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault('default', list)
        super().__init__(*args, **kwargs)

    def unmarshal(self, values: Iterable[Any]) -> List[Any]:
        return [super(JsonArray, self).unmarshal(value) for value in values]

    def marshal(self, values: Iterable[Any]) -> List[Any]:
        return [super(JsonArray, self).marshal(value) for value in values]


def _flatten_slots(cls, slots: Optional[Iterable[str]] = None) -> Set[str]:
    if slots is None:
        slots = set()

    slots.update(getattr(cls, '__slots__', ()))

    for base in cls.__bases__:
        _flatten_slots(base, slots)

    return slots


class JsonObjectMeta(Type[T]):
    __template__: JsonTemplate
    def __new__(
        cls, name: str, bases: Tuple[type, ...], attrs: Dict[str, Any],
        template: Optional[JsonTemplate] = None
    ) -> JsonObjectMeta[T]:
        external_slots = set()
        for base in bases:
            _flatten_slots(base, external_slots)

        slots = tuple(attrs.get('__slots__', ()))
        if template is not None:
            fields = template.fields
            slots += tuple(field for field in fields
                           if field not in slots
                           and field not in external_slots)

        attrs['__slots__'] = slots
        attrs['__template__'] = template

        return type.__new__(cls, name, bases, attrs)


class JsonObject(metaclass=JsonObjectMeta):
    __slots__ = ('__fields__',)
    __fields__: Set[str]
    __template__: ClassVar[Optional[JsonTemplate]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    @classmethod
    def unmarshal(cls: Type[OT], data: Union[Dict[str, Any], bytes, bytearray, memoryview, str, None] = None,
                  *args: Any, **kwargs: Any
    ) -> OT:
        if cls.__template__ is None:
            raise NotImplementedError

        if isinstance(data, (bytes, bytearray, memoryview, str)):
            data = json.loads(data)

        self = cls.__new__(cls)
        self.__fields__ = set()
        cls.__init__(self, *args, **kwargs)
        self.update(data or {}, set_defaults=True)

        return self

    def update(self, *args: Any, **kwargs: Any) -> None:
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.update(self, *args, **kwargs)

    def to_dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.to_dict(self, *args, **kwargs)

    def marshal(self, *args: Any, **kwargs: Any) -> str:
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.marshal(self, *args, **kwargs)
