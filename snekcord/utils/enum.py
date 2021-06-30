__all__ = ('Enum',)


class Enum:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __init_subclass__(cls):
        cls._enum_names_ = {}
        cls._enum_values_ = {}

        for key, value in cls.__dict__.items():
            if (not key.startswith('_')
                    and isinstance(value, cls._enum_type_)):
                enum = cls(key, value)
                cls._enum_names_[key] = enum
                cls._enum_values_[value] = enum

    def __class_getitem__(cls, klass):
        if isinstance(klass, type):
            return type(cls.__name__, (cls,), {'_enum_type_': klass})
        return klass

    def __repr__(self):
        return (f'<{self.__class__.__name__} name={self.name}, value={self.value!r}>')

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self._enum_type_):
            return NotImplemented

        return self.value == value

    def __ne__(self, value):
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self._enum_type_):
            return NotImplemented

        return self.value != value

    @classmethod
    def get_enum(cls, value):
        try:
            return cls._enum_names_[value]
        except KeyError:
            return cls('undefined', value)

    @classmethod
    def get_value(cls, enum):
        if isinstance(enum, cls):
            return enum.value
        elif isinstance(enum, cls._enum_type_):
            return enum
        raise ValueError(f'{enum!r} is not a valid {cls.__name__}')
