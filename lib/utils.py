import json

from datetime import datetime

SNOWFLAKE_MINIMUM_BIT_LENGTH = 51
SNOWFLAKE_MAXIMUM_BIT_LENGTH = 111
DISCORD_EPOCH = 1420070400000

class JsonStructure:
    # inspired by Go's encoding/json module
    def __init_subclass__(cls):
        if not hasattr(cls, 'json_fields'):
            cls.json_fields = {}
        for name, value in dict(cls.__dict__).items():
            if isinstance(value, JsonField):
                cls.json_fields[name] = value
                value._attr_name = name
                delattr(cls, name)

    @classmethod
    def unmarshal(cls, data, *args, init_class=True, **kwargs):
        if isinstance(data, (str, bytes, bytearray)):
            data = json.loads(data)

        self = object.__new__(cls)
        for name, field in self.json_fields.items():
            try:
                value = field.unmarshal(data[field.name])
                setattr(self, field._attr_name, value)
            except Exception as e:
                print(e)
                setattr(self, field._attr_name, field.default)
        if init_class:
            self.__init__(*args, **kwargs)
        return self

    def to_dict(self):
        dct = {}
        for name, field in self.json_fields.items():
            try:
                attr = getattr(self, name)
                value = field.marshal(attr)
                if value is None and field.omitemoty:
                    continue
                dct[name] = value
            except AttributeError:
                continue
        return dct

    def marshal(self):
        return json.dumps(self.to_dict())

class JsonField:
    def __init__(self, key, unmarshal_callable=None, marshal_callable=None, default=None, struct=None, init_struct_class=True, omitemoty=True):
        if struct is not None:
            self.unmarshal_callable = lambda *args, **kwargs: struct.unmarshal(*args, **kwargs, init_class=init_struct_class)
            self.marshal_callable = struct.to_dict
        else:
            self.unmarshal_callable = unmarshal_callable
            self.marshal_callable = marshal_callable
        self.name = key
        self.default = default

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
        if not SNOWFLAKE_MINIMUM_BIT_LENGTH <= self.bit_length() <= SNOWFLAKE_MAXIMUM_BIT_LENGTH:
            raise ValueError('Snowflake\'s bit length should be {} to {}'.format(SNOWFLAKE_MINIMUM_BIT_LENGTH, SNOWFLAKE_MAXIMUM_BIT_LENGTH))
        return self

    @property
    def datetime(self):
        return datetime.fromtimestamp(((self >> 22) + DISCORD_EPOCH) / 1000)

    @property
    def worker_id(self):
        return (self & 0x3E0000) >> 17

    @property
    def process_id(self):
        return (self & 0x1F000) >> 12

    @property
    def increment(self):
        return self & 0xFFF