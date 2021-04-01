import json
import struct
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict

JSON = Dict[str, Any]

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
        cls.__json_fields__ = cls.__json_fields__.copy()
        for bcls in cls.__bases__:
            if hasattr(bcls, '__json_fields__'):
                cls.__json_fields__.update(bcls.__json_fields__)

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
    def __init__(self, *args, **kwargs):
        default = kwargs.pop('default', [])
        super().__init__(*args, **kwargs, default=default)

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


class CType:
    def __init__(self, format_char):
        self.format_char = format_char

    @property
    def size(self):
        return struct.calcsize(self.format_char)


class cstruct:
    Pad = CType('x')
    Char = CType('c')
    SignedChar = CType('b')
    UnsignedChar = CType('B')
    Bool = CType('?')
    Short = CType('h')
    UnsignedShort = CType('H')
    Int = CType('i')
    UnsignedInt = CType('I')
    Long = CType('l')
    UnsignedLong = CType('L')
    LongLong = CType('q')
    UnsignedLongLong = CType('Q')
    SizeT = CType('n')
    SSizeT = CType('N')
    HalfPrecisionFloat = CType('e')
    Float = CType('f')
    Double = CType('d')
    String = CType('s')
    PascalString = CType('p')
    VoidP = CType('P')

    def __init_subclass__(cls):
        cls.fields = OrderedDict()

        for name, annotation in cls.__annotations__.items():
            if isinstance(annotation, CType):
                cls.fields[name] = annotation

        format_string = ''.join(tp.format_char for tp in cls.fields.values())
        cls.struct = struct.Struct(cls.byteorder + format_string)

    @classmethod
    def _get_args(cls, kwargs, name):
        args = []

        for field in cls.fields:
            try:
                args.append(kwargs.pop(field))
            except KeyError:
                msg = '"{}" missing required keyword argument "{}"'.format(name, field)
                raise TypeError(msg) from None

        if kwargs:
            arg = next(iter(kwargs))
            msg = '"{}" received unexpected keyword argument, "{}"'.format(name, arg)
            raise TypeError(msg)

        return args

    @classmethod
    def _create(cls, **values):
        self = object.__new__(cls)

        self.fields = values

        for name, value in values.items():
            setattr(self, name, value)

        return self

    @classmethod
    def iter_unpack(cls, buffer):
        return cls.struct.iter_unpack(buffer)

    @classmethod
    def unpack(cls, buffer):
        values = cls.struct.unpack(buffer)
        return cls._create(**dict(zip(cls.fields, values)))

    @classmethod
    def unpack_from(cls, buffer, offset=0):
        values = cls.struct.unpack_from(buffer, offset)
        return cls._create(**dict(zip(cls.fields, values)))

    @classmethod
    def pack(cls, **kwargs):
        args = cls._get_args(kwargs, 'pack')
        return cls.struct.pack(*args)

    @classmethod
    def pack_into(cls, buffer, offset, **kwargs):
        args = cls._get_args(kwargs, 'pack_into')
        return cls.struct.pack_into(buffer, offset, *args)


class Snowflake(int):
    __slots__ = ()

    @classmethod
    def build(cls, timestamp=None, worker_id=0, process_id=0, increment=0):
        if timestamp is None:
            timestamp = datetime.now().timestamp()

        timestamp *= 1000
        timestamp -= DISCORD_EPOCH

        snowflake = 0
        snowflake |= int(timestamp) << 22
        snowflake |= worker_id << 17
        snowflake |= process_id << 12
        snowflake |= increment

        return cls(snowflake)

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
    from .structures import BaseObject

    if isinstance(value, BaseObject):
        value = value.id

    try:
        value = Snowflake(value)
    except (ValueError, TypeError):
        pass

    return value
