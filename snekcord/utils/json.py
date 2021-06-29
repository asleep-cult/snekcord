import json

__all__ = ('JsonField', 'JsonArray', 'JsonObject')


class JsonObject:
    __slots__ = ('_json_data_',)

    @classmethod
    def unmarshal(cls, data=None, **kwargs):
        if isinstance(data, (bytes, bytearray, memoryview, str)):
            data = json.loads(data)

        self = cls.__new__(cls)
        self._json_data_ = {}
        cls.__init__(self, **kwargs)

        if data is not None:
            self.update(data)

        return self

    def update(self, data):
        self._json_data_.update(data)

    def to_dict(self):
        return self._json_data_

    def marshal(self, *args, **kwargs):
        return json.dumps(self._json_data_, *args, **kwargs)


class JsonField:
    def __init__(self, key, unmarshaler=None, object=None, default=None):
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
            if callable(self.default):
                return self.default()
            return self.default

        if self._unmarshaler is not None:
            value = self._unmsrshal_(value)

        return value

    def __set__(self, instance, value):
        raise AttributeError(f'Cannot set attribute {self.name!r}')

    def __delete__(self, instance):
        raise AttributeError(f'Cannot delete attribute {self.name!r}')

    def _unmsrshal_(self, value):
        if self._unmarshaler is not None:
            return self._unmarshaler(value)
        return value

    def unmarshaler(self, func):
        self._unmarshaler = func
        return self


class JsonArray(JsonField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', list)
        super().__init__(*args, **kwargs)

    def _unmarshal_(self, values):
        return [super(JsonArray, self).unmarshal(value) for value in values]
