__all__ = ('Enum',)


class Enum:
    __enum_type__ = object

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
        if not isinstance(value, self.__class__):
            return NotImplemented
        return self.value == value.value

    def __ne__(self, value):
        if not isinstance(value, self.__class__):
            return NotImplemented
        return self.value != value.value

    @classmethod
    def try_enum(cls, value):
        try:
            return cls.__enum_values__[value]
        except KeyError:
            return cls('undefined', value)

    def valuegetter(self):
        return self.value
