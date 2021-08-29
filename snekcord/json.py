import json

from .undefined import undefined


class JsonField:
    __slots__ = ('key', 'unmarshaler', 'owner', 'name')

    def __init__(self, key, unmarshaler=None, *, object=None):
        self.key = key
        self.unmarshaler = unmarshaler

        if object is not None:
            self.unmarshaler = object.unmarshal

        self.owner = None
        self.name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = self.get(instance, undefined)
        if value is undefined:
            raise AttributeError(f'{owner.__name__} object is missing field {self.name!r}')

        return value

    def __set__(self, instance, value):
        raise AttributeError(f'{self.qualname()} does not support assignment')

    def __delete__(self, instance):
        raise AttributeError(f'{self.qualname()} does not support deletion')

    def qualname(self):
        return f'{self.owner.__name__}.{self.name}'

    def get(self, instance, default=None):
        if not isinstance(instance, self.owner):
            raise TypeError(
                f'{self.qualname()}.get() expects {self.owner.__name__}, '
                f'received {instance.__class__.__name__}'
            )

        try:
            value = instance._json_data_[self.key]

            if self.unmarshaler is not None:
                value = self.unmarshaler(value)

            return value
        except KeyError:
            return default

    def exists(self, instance):
        if not isinstance(instance, self.owner):
            raise TypeError(
                f'{self.qualname()}.exists() expects {self.owner.__name__}, '
                f'received {instance.__class__.__name__}'
            )

        return self.key in instance._json_data_


class JsonArray(JsonField):
    def get(self, instance, default=None):
        if not isinstance(instance, self.owner):
            raise TypeError(
                f'{self.qualname()}.get() expects {self.owner.__name__}, '
                f'received {instance.__class__.__name__}'
            )

        try:
            values = instance._json_data_[self.key]

            if self.unmarshaler is not None:
                values = [self.unmarshaler(value) for value in values]

            return values
        except KeyError:
            return default


class JsonObjectMeta(type):
    def __call__(cls, *args, **kwargs):
        self = cls.__new__(cls)
        self._json_data_ = [undefined] * len(cls._json_fields_)

        ret = cls.__init__(self, *args, **kwargs)
        if ret is not None:
            raise TypeError(f'__init__() should return None, not {ret.__class__.__name__}')

        return self


class JsonObject(metaclass=JsonObjectMeta):
    __slots__ = ('_json_data_',)

    def __init_subclass__(cls):
        cls._json_fields_ = {}

        for name, value in cls.__dict__.items():
            if isinstance(value, JsonField):
                value.owner = cls
                value.name = name

                cls._json_fields_[name] = value

    def __contains__(self, key):
        return key in self._json_fields_

    def __getitem__(self, key):
        field = self._json_fields_[key]

        value = field.get(self, undefined)
        if value is undefined:
            raise KeyError(key)

        return value

    @classmethod
    def unmarshal(cls, data, **kwargs):
        if isinstance(data, (str, bytes)):
            data = json.loads(data)

        self = cls(**kwargs)
        self.update(data)
        return self

    def get(self, key, default=None):
        if key in self._json_fields_:
            return self._json_fields_[key].get(self, default)
        return default

    def to_dict(self):
        return self._json_data_.copy()

    def marshal(self, *args, **kwargs):
        return json.dumps(self._json_data_, *args, **kwargs)

    def update(self, data):
        self._json_data_.update(data)
