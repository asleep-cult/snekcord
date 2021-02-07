import json
from datetime import datetime

from typing import Dict, Any

JSON = Dict[str, Any]
SNOWFLAKE_MINIMUM_BIT_LENGTH = 51
SNOWFLAKE_MAXIMUM_BIT_LENGTH = 111
DISCORD_EPOCH = 1420070400000


class _Undefined:
    def __bool__(self):
        return False

    def __repr__(self):
        return '<undefined>'


undefined = _Undefined()


class JsonStructure:
    # inspired by Go's encoding/json module

    __json_fields__: dict

    def __init_subclass__(cls):
        assert hasattr(cls, '__json_fields__')

    @classmethod
    def unmarshal(cls, data, *args, init_class=True, **kwargs):
        if isinstance(data, (str, bytes, bytearray)):
            data = json.loads(data)

        self = object.__new__(cls)

        if init_class:
            self.__init__(*args, **kwargs)

        self._update(data, set_default=True)

        return self

    def _update(self, data, set_default=False):
        for name, field in self.__json_fields__.items():
            try:
                value = field.unmarshal(data[field.name])
                setattr(self, name, value)
            except BaseException:
                if set_default:
                    setattr(self, name, field.default)

    def to_dict(self, cls=None):
        dct = {}

        if cls is not None:
            json_fields = cls.__json_fields__
        else:
            json_fields = self.__json_fields__

        for name, field in json_fields.items():
            try:
                attr = getattr(self, name)
                if attr is None and field.omitemoty:
                    continue
                try:
                    value = field.marshal(attr)
                except BaseException:
                    continue
                if value is None and field.omitemoty:
                    continue
                dct[field.name] = value
            except AttributeError:
                continue
        return dct

    def marshal(self):
        return json.dumps(self.to_dict())


class JsonField:
    def __init__(
        self,
        key,
        unmarshal_callable=None,
        marshal_callable=None,
        default=None,
        struct=None,
        init_struct_class=True,
        omitemoty=False
    ):
        if struct is not None:
            self.unmarshal_callable = lambda *args, **kwargs: struct.unmarshal(
                *args, **kwargs, init_class=init_struct_class)
            self.marshal_callable = struct.to_dict
        else:
            self.unmarshal_callable = unmarshal_callable
            self.marshal_callable = marshal_callable
        self.name = key
        self.default = default
        self.omitempty = omitemoty

    def unmarshal(self, data):
        if self.unmarshal_callable is None:
            return data
        return self.unmarshal_callable(data)

    def marshal(self, data):
        if self.marshal_callable is None:
            return data
        return self.marshal_callable(data)


class JsonArray(JsonField):
    def unmarshal(self, data):
        items = []
        for item in data:
            items.append(super().unmarshal(item))
        return items

    def marshal(self, data):
        items = []
        for item in data:
            items.append(super().marshal(item))
        return items


class Snowflake(int):
    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        self = int.__new__(cls, *args, **kwargs)
        if not (
            SNOWFLAKE_MINIMUM_BIT_LENGTH <=
            self.bit_length() <=
            SNOWFLAKE_MAXIMUM_BIT_LENGTH
        ):
            raise ValueError(
                'Snowflake\'s bit length should be {} to {}'.format(
                    SNOWFLAKE_MINIMUM_BIT_LENGTH, SNOWFLAKE_MAXIMUM_BIT_LENGTH
                )
            )
        return self

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(((self >> 22) + DISCORD_EPOCH) / 1000)

    @property
    def worker_id(self) -> int:
        return (self & 0x3E0000) >> 17

    @property
    def process_id(self) -> int:
        return (self & 0x1F000) >> 12

    @property
    def increment(self) -> int:
        return self & 0xFFF


def _try_snowflake(value):
    from .bases import BaseObject

    if isinstance(value, BaseObject):
        value = value.id

    try:
        value = Snowflake(value)
    except (ValueError, TypeError):
        pass
    return value
