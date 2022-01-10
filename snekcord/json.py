import json
from collections.abc import Iterable
from ctypes import py_object as _py_object
from typing import Any, Dict

from .exceptions import InvalidFieldError, MissingFieldError

JSONData = Dict[str, Any]


class JSONEncoder(json.JSONEncoder):
    """A subclass of json.JSONEncoder that treats any iterable object as an array."""

    def __init__(self, *, separators=(',', ':'), **kwargs):
        super().__init__(separators=separators, **kwargs)

    def default(self, obj):
        if isinstance(obj, Iterable):
            return tuple(obj)
        else:
            return super().default(obj)


def load_json(*args, **kwargs):
    """Equivalent to json.loads."""
    return json.loads(*args, **kwargs)


def dump_json(obj, *, separators=(',', ':'), **kwargs):
    """Equivalent to json.dumps using the library's JSONEncoder class."""
    return json.dumps(obj, separators=separators, **kwargs, cls=JSONEncoder)


class _JSONDescriptor:
    def __init__(self, key, unmarshaler=None, *, object=None, repr=False):
        self.key = key
        self.unmarshaler = unmarshaler
        self.object = object
        self.repr = repr

        self._bound = False

    def __repr__(self):
        attrs = [
            ('key', self.key),
            ('unmarshaler', self.unmarshaler),
            ('object', self.object),
            ('repr', self.repr),
        ]
        params = ', '.join(f'{key}={value!r}' for key, value in attrs)
        return f'{self.__class__.__name__}({params})'

    def _qualname(self, instance):
        return f'{instance.__class__.__name__}.{self._name}'

    def construct(self, value):
        return value

    def deconstruct(self, value):
        return value

    def unmarshal(self, value):
        return value

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if not self._bound:
            raise RuntimeError('__get__() called on unbound JSONField')

        try:
            value = instance._json_slots_[self._position]
        except ValueError:
            raise MissingFieldError(self, instance) from None

        if value is None:
            return None

        return self.unmarshal(value)

    def __set__(self, instance, value):
        if not self._bound:
            raise RuntimeError('__set__() called on unbound JSONField')

        raise AttributeError(f'{self._qualname(instance)} does not support assignment')

    def __delete__(self, instance):
        if not self._bound:
            raise RuntimeError('__delete__() called on unbound JSONField')

        raise AttributeError(f'{self._qualname(instance)} does not support deletion')

    def bind(self, name, position):
        clone = object.__new__(self.__class__)
        clone.key = self.key
        clone.unmarshaler = self.unmarshaler
        clone.object = self.object
        clone.repr = self.repr

        clone._bound = True
        clone._name = name
        clone._position = position

        return clone


class JSONField(_JSONDescriptor):
    def construct(self, value):
        if self.object is None:
            return value

        if not isinstance(value, dict):
            raise InvalidFieldError(self)

        return self.object.unmarshal(value)

    def deconstruct(self, value):
        if self.object is None:
            return value

        if not isinstance(value, self.object):
            raise InvalidFieldError(self)

        return value.to_dict()

    def unmarshal(self, value):
        if self.unmarshaler is None:
            return value

        return self.unmarshaler(value)


class JSONArray(_JSONDescriptor):
    def construct(self, values):
        if not isinstance(values, (list, tuple)):
            raise InvalidFieldError(self)

        if self.object is None:
            return tuple(values)

        return tuple(self.object.unmarshal(value) for value in values)

    def deconstruct(self, values):
        if not isinstance(values, tuple):
            raise InvalidFieldError(self)

        if self.object is None:
            return values

        return tuple(value.to_dict() for value in values)

    def unmarshal(self, values):
        if self.unmarshaler is None:
            return values

        return tuple(self.unmarshaler(value) for value in values)


class JSONObjectMeta(type):
    def __new__(cls, name, bases, namespace):
        json_fields = {}

        for key, value in namespace.items():
            if isinstance(value, _JSONDescriptor):
                json_fields[key] = value.bind(key, len(json_fields))

        namespace['_json_fields_'] = json_fields

        return type.__new__(cls, name, bases, namespace)


class JSONObject(metaclass=JSONObjectMeta):
    __slots__ = ('_json_slots_',)

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self._json_slots_ = (_py_object * len(cls._json_fields_))()
        return self

    @classmethod
    def unmarshal(cls, data, **kwargs):
        self = cls.__new__(cls)
        self.update(data)

        ret = cls.__init__(self, **kwargs)
        if ret is not None:
            raise TypeError(f'__init__() should return None, not {ret.__class__.__name__}')

        return self

    def __repr__(self):
        attrs = []
        for name, field in self._json_fields_.items():
            if field.repr:
                attrs.append((name, getattr(self, name)))

        if not attrs:
            return f'<{self.__class__.__name__}>'

        inner = ', '.join(f'{name}={value}' for name, value in attrs)
        return f'<{self.__class__.__name__} {inner}>'

    def update(self, data):
        if isinstance(data, (str, bytes)):
            data = load_json(data)

        if not isinstance(data, dict):
            raise TypeError(f'data should be a dict, got {data.__class__.__name__}')

        for field in self._json_fields_.values():
            try:
                value = data[field.key]
            except KeyError:
                continue

            if value is not None:
                value = field.construct(value)

            self._json_slots_[field._position] = value

    def to_dict(self):
        data = {}

        for field in self._json_fields_.values():
            try:
                value = self._json_slots_[field._position]
            except ValueError:
                continue

            if value is not None:
                value = field.deconstruct(value)

            data[field.key] = value

        return data

    def marshal(self, *args, **kwargs):
        return dump_json(self.to_dict(), *args, **kwargs)
