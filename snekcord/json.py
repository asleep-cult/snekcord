import json

from .exceptions import PartialObjectError
from .undefined import undefined

__all__ = ('JsonObject', 'JsonField', 'JsonArray')


class JsonObjectMeta(type):
    def __call__(cls, *args, **kwargs):
        self = super().__call__(*args, **kwargs)
        self._json_data_ = {}
        return self


class JsonObject(metaclass=JsonObjectMeta):
    __slots__ = ('_json_data_',)

    @classmethod
    def unmarshal(cls, data=None, **kwargs):
        if isinstance(data, (bytes, bytearray, memoryview, str)):
            data = json.loads(data)

        self = cls(**kwargs)

        if data is not None:
            self.update(data)

        return self

    def update(self, data):
        self._json_data_.update(data)
        return self

    def to_dict(self):
        return self._json_data_.copy()

    def marshal(self, *args, **kwargs):
        return json.dumps(self._json_data_, *args, **kwargs)


class JsonField:
    def __init__(self, key, unmarshaler=None, object=None, default=undefined):
        self.key = key
        self.object = object
        self.default = default

        if self.object is not None:
            self._unmarshaler = self.object.unmarshal
        else:
            self._unmarshaler = unmarshaler

        self.name = None

    def __set_name__(self, owner, name):
        if not issubclass(owner, JsonObject):
            raise TypeError(f'{self.__class__.__name__!r} can only be used with JsonObject')
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        try:
            value = instance._json_data_[self.key]
        except KeyError:
            if self.default is undefined:
                raise PartialObjectError(
                    f'{instance.__class__.__name__} object is missing field {self.name!r}'
                ) from None

            if callable(self.default):
                value = self.default()
            else:
                value = self.default

        return self._unmarshal_(value)

    def __set__(self, instance, value):
        raise AttributeError(f'Cannot set attribute {self.name!r}')

    def __delete__(self, instance):
        raise AttributeError(f'Cannot delete attribute {self.name!r}')

    def _unmarshal_(self, value):
        if self._unmarshaler is not None:
            return self._unmarshaler(value)
        return value


class JsonArray(JsonField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', list)
        super().__init__(*args, **kwargs)

    def _unmarshal_(self, values):
        return [super(JsonArray, self)._unmarshal_(value) for value in values]
