__all__ = ('Flag', 'Bitset')


class Flag:
    def __init__(self, position):
        self.position = position

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return ((instance.value >> self.position) & 1) != 0

    def __set__(self, instance, value):
        if value:
            instance.value |= (1 << self.position)
        else:
            instance.value &= ~(1 << self.position)

    def __delete__(self, instance):
        instance.value &= ~(1 << self.position)


class Bitset:
    def __init__(self, **kwargs):
        self.value = 0
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls):
        cls._length_ = 0
        cls._flags_ = {}

        for name, value in cls.__dict__.items():
            if isinstance(value, Flag):
                cls._flags_[name] = value

                if value.position > cls._length_:
                    cls._length_ = value.position

        cls._length_ += 1

    def __iter__(self):
        for flag in self._flags__:
            yield getattr(self, flag)

    def __index__(self):
        return self.value

    @classmethod
    def all(cls):
        return cls.from_value((1 << cls._length_) - 1)

    @classmethod
    def none(cls):
        return cls.from_value(0)

    @classmethod
    def from_value(cls, value):
        self = cls.__new__(cls)
        self.value = value
        return self

    def to_dict(self):
        return dict(zip(self._flags_, self))
