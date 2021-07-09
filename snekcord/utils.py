import json
from datetime import datetime

from .exceptions import PartialObjectError

__all__ = ('undefined', 'JsonField', 'JsonArray', 'JsonObject', 'Snowflake')

_validate_keys = None


class Undefined:
    def __bool__(self):
        return False

    def __repr__(self):
        return '<undefined>'


undefined = Undefined()


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
        return self

    def to_dict(self):
        return self._json_data_

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


class JsonArray(JsonField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', list)
        super().__init__(*args, **kwargs)

    def _unmarshal_(self, values):
        return [super(JsonArray, self).unmarshal(value) for value in values]


class Snowflake(int):
    __slots__ = ()

    SNOWFLAKE_EPOCH = 1420070400000

    TIMESTAMP_SHIFT = 22
    WORKER_ID_SHIFT = 17
    PROCESS_ID_SHIFT = 12

    WORKER_ID_MASK = 0x3E0000
    PROCESS_ID_MASK = 0x1F000
    INCREMENT_MASK = 0xFFF

    @classmethod
    def build(cls, timestamp=None, worker_id=0, process_id=0, increment=0):
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        elif isinstance(timestamp, datetime):
            timestamp = timestamp.timestamp()

        timestamp = int((timestamp * 1000) - cls.SNOWFLAKE_EPOCH)

        return cls((timestamp << cls.TIMESTAMP_SHIFT)
                   | (worker_id << cls.WORKER_ID_SHIFT)
                   | (process_id << cls.PROCESS_ID_SHIFT)
                   | increment)

    @classmethod
    def try_snowflake(cls, obj, *, allow_datetime=False):
        from .objects.baseobject import BaseObject

        if isinstance(obj, BaseObject):
            if isinstance(obj.id, cls):
                return obj.id
            else:
                raise ValueError(f'Failed to convert {obj!r} to a Snowflake')
        elif allow_datetime:
            if isinstance(obj, datetime):
                return cls.build(obj.timestamp())

        try:
            return cls(obj)
        except Exception:
            raise ValueError(f'Failed to convert {obj!r} to a Snowflake')

    @classmethod
    def try_snowflake_set(cls, objs, *, allow_datetime=False):
        return {cls.try_snowflake(obj, allow_datetime=allow_datetime) for obj in objs}

    @property
    def timestamp(self):
        return ((self >> self.TIMESTAMP_SHIFT) + self.SNOWFLAKE_EPOCH) / 1000

    @property
    def worker_id(self):
        return (self & self.WORKER_ID_MASK) >> self.WORKER_ID_SHIFT

    @property
    def process_id(self):
        return (self & self.PROCESS_ID_MASK) >> self.PROCESS_ID_SHIFT

    @property
    def increment(self):
        return self & self.INCREMENT_MASK

    def as_datetime(self):
        return datetime.fromtimestamp(self.timestamp)
