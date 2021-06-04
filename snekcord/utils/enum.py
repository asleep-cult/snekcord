__all__ = ('Enum',)


class EnumMeta(type):
    def __new__(mcs, name, bases, attrs, *, type):
        attrs['__enum_type__'] = type
        return super().__new__(mcs, name, bases, attrs)


class Enum(metaclass=EnumMeta, type=object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __init_subclass__(cls):
        cls.__enum_names__ = {}
        cls.__enum_values__ = {}

        for key, value in cls.__dict__.items():
            if (not key.startswith('_')
                    and isinstance(value, cls.__enum_type__)):
                enum = cls(key, value)
                cls.__enum_names__[key] = enum
                cls.__enum_values__[value] = enum

    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.name}, '
                f'value={self.value!r})')

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self.__enum_type__):
            return NotImplemented

        return self.value == value

    def __ne__(self, value):
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self.__enum_type__):
            return NotImplemented

        return self.value != value

    @classmethod
    def get_enum(cls, value):
        try:
            return cls.__enum_values__[value]
        except KeyError:
            return cls('undefined', value)

    @classmethod
    def get_value(cls, enum):
        if isinstance(enum, cls):
            return enum.value
        elif isinstance(enum, cls.__enum_class__):
            return enum
        raise ValueError(
            f'{enum!r} is not a valid {cls.__name__}')
