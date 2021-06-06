from __future__ import annotations

import json
import typing as t

from ..typing import AnyCallable, Json

__all__ = ('JsonTemplate', 'JsonField', 'JsonArray', 'JsonObject')

T = t.TypeVar('T')
OT = t.TypeVar('OT', bound='JsonObject')


class JsonTemplate:
    local_fields: dict[str, JsonField]
    fields: dict[str, JsonField]

    def __init__(self, *,
                 __extends__: tuple[JsonTemplate, ...] = (),
                 **fields: JsonField) -> None:
        self.local_fields = fields
        self.fields = self.local_fields.copy()

        for template in __extends__:
            self.fields.update(template.fields)

    def update(self, obj: JsonObject, data: Json, *,
               set_defaults: bool = False) -> None:
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

    def to_dict(self, obj: JsonObject) -> Json:
        data: Json = {}

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

    def marshal(self, obj: JsonObject, *args: t.Any, **kwargs: t.Any) -> str:
        return json.dumps(self.to_dict(obj), *args, **kwargs)

    def default_object(self, name: str = 'GenericObject') -> type[JsonObject]:
        return JsonObjectMeta(name, (JsonObject,), {},
                              template=self)  # type: ignore


class JsonField:
    key: str
    object: type[JsonObject] | None
    _default: t.Any
    _unmarshal: AnyCallable | None
    _marshal: AnyCallable | None

    def __init__(self, key: str, unmarshal: AnyCallable | None = None,
                 marshal: AnyCallable | None = None,
                 object: type[JsonObject] | None = None,
                 default: t.Any = None) -> None:
        self.key = key
        self.object = object
        self._default = default

        if self.object is not None:
            assert self.object.__template__ is not None

            self._unmarshal = self.object.unmarshal
            self._marshal = self.object.__template__.to_dict
        else:
            self._unmarshal = unmarshal
            self._marshal = marshal

    def unmarshal(self, value: t.Any) -> t.Any:
        if self._unmarshal is not None:
            value = self._unmarshal(value)
        return value

    def marshal(self, value: t.Any) -> t.Any:
        if self._marshal is not None:
            value = self._marshal(value)
        return value

    def default(self) -> t.Any:
        if callable(self._default):
            return self._default()
        return self._default


class JsonArray(JsonField):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        kwargs.setdefault('default', list)
        super().__init__(*args, **kwargs)

    def unmarshal(self, value: t.Iterable[t.Any]) -> list[t.Any]:
        return [super(JsonArray, self).unmarshal(val) for val in value]

    def marshal(self, value: t.Iterable[t.Any]) -> list[t.Any]:
        return [super(JsonArray, self).marshal(val) for val in value]


def _flatten_slots(cls: type, slots: set[str] | None = None) -> set[str]:
    if slots is None:
        slots = set()

    slots.update(getattr(cls, '__slots__', ()))

    for base in cls.__bases__:
        _flatten_slots(base, slots)

    return slots


class JsonObjectMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...],
                attrs: dict[str, t.Any],
                template: JsonTemplate | None = None) -> JsonObjectMeta:
        external_slots: set[str] = set()
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
    __fields__: set[str]
    __template__: t.ClassVar[JsonTemplate | None]

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        pass

    @classmethod
    def unmarshal(cls: type[OT], data: Json | t.ByteString | None = None,
                  *args: t.Any, **kwargs: t.Any) -> OT:
        if cls.__template__ is None:
            raise NotImplementedError

        if isinstance(data, (bytes, bytearray, memoryview, str)):
            data = json.loads(data)

        self = cls.__new__(cls)
        self.__fields__ = set()
        cls.__init__(self, *args, **kwargs)
        self.update(data or {}, set_defaults=True)

        return self

    def update(self, *args: t.Any, **kwargs: t.Any) -> None:
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.update(self, *args, **kwargs)

    def to_dict(self, *args: t.Any, **kwargs: t.Any) -> Json:
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.to_dict(self, *args, **kwargs)

    def marshal(self, *args: t.Any, **kwargs: t.Any) -> str:
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.marshal(self, *args, **kwargs)
