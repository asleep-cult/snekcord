__all__ = ('Bitset', 'Flag', 'NamedBitset')


class Bitset:
    def __init__(self, value=0):
        self.value = value

    def _noamalize_indice(self, indice):
        if not isinstance(indice, int):
            raise TypeError(f'{self.__class__.__name__} indices must be '
                            f'integers, got {indice.__class__.__name__}')

        return indice

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value == other.value

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length != other.length or self.value != other.value

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value > other.value

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value >= other.value

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value < other.value

    def __le__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.length == other.length and self.value <= other.value

    def __index__(self):
        return self.value

    def __len__(self):
        return self.length

    def __getitem__(self, position):
        return (self.value >> self._noamalize_indice(position)) & 1

    def __setitem__(self, position, value):
        if value:
            self.value |= (1 << self._noamalize_indice(position))
        else:
            del self[position]

    def __delitem__(self, position):
        self.value &= ~(1 << self._noamalize_indice(position))


class Flag:
    def __init__(self, position):
        self.position = position

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance[self.position]

    def __set__(self, instance, value):
        instance[self.position] = value

    def __delete__(self, instance):
        del instance[self.position]


class NamedBitset(Bitset):
    def __init__(self, **kwargs):
        super().__init__()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls):
        cls.__length__ = 0
        cls.__bitset_flags__ = {}
        for name, value in cls.__dict__.items():
            if isinstance(value, Flag):
                if value.position > cls.__length__:
                    cls.__length__ = value.position
                cls.__bitset_flags__[name] = value

        cls.__length__ += 1

    @classmethod
    def all(cls):
        return cls.from_value((1 << cls.__length__) - 1)

    @classmethod
    def none(cls):
        return cls.from_value(0)

    @classmethod
    def from_value(cls, value):
        self = cls.__new__(cls)
        Bitset.__init__(self, int(value))
        return self

    def get_value(self):
        return self.value

    def to_dict(self):
        return dict(zip(self.__bitset_flags__, self))
