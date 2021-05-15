import weakref

from ..utils.snowflake import Snowflake


class BaseMapping:
    def __iter__(self):
        return iter(list(self.values()))

    def __reversed__(self):
        return reversed(list(self.items()))

    @classmethod
    def for_type(cls, klass):
        return type('Mapping', (cls, klass), {})


class BaseSnowflakeMapping(BaseMapping):
    def __setitem__(self, key, value):
        return super().__setitem__(Snowflake.try_snowflake(key), value)

    def __getitem__(self, key):
        return super().__getitem__(Snowflake.try_snowflake(key))

    def __delitem__(self, key):
        return super().__delitem__(Snowflake.try_snowflake(key))

    def __contains__(self, key):
        return Snowflake.try_snowflake(key) in self

    def get(self, key, default=None):
        return super().get(Snowflake.try_snowflake(key), default)

    def pop(self, key, *args, **kwargs):
        return super().pop(Snowflake.try_snowflake(key), *args, **kwargs)


Mapping = BaseMapping.for_type(dict)
SnowflakeMapping = BaseSnowflakeMapping.for_type(dict)
WeakValueMapping = BaseMapping.for_type(weakref.WeakValueDictionary)
WeakValueSnowflakeMapping = (
    SnowflakeMapping.for_type(weakref.WeakValueDictionary)
)


class _StateCommon:
    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True

    def find(self, func):
        for item in self:
            if func(item):
                return item


class BaseState(_StateCommon):
    __container__ = Mapping
    __recycled_container__ = WeakValueMapping
    __maxsize__ = 0
    __replace__ = True

    def __init__(self, *, manager):
        self._items = self.__container__()
        self._recycle_bin = self.__recycled_container__()
        self.manager = manager

    def __repr__(self):
        return (f'{self.__class__.__name__}(length={len(self)}, '
                f'recycled={len(self._recycle_bin)})')

    @classmethod
    def set_maxsize(cls, maxsize):
        cls.__maxsize__ = maxsize

    @classmethod
    def get_maxsize(cls):
        return cls.__maxsize__

    @classmethod
    def set_replace(cls, replace):
        cls.__replace__ = replace

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return self._items.__iter__()

    def __reversed__(self):
        return self._items.__reversed__()

    def set(self, key, value):
        if self.__maxsize__ < 0:
            return False

        if (
            self.__maxsize__ != 0
            and len(self) >= self.__maxsize__
        ):
            if not self.__replace__:
                return False

            self.popitem().uncache()

        self._items.__setitem__(key, value)
        return True

    __setitem__ = set

    def __getitem__(self, key):
        return self._items.__getitem__(key)

    def __delitem__(self, key):
        return self._items.__delitem__(key)

    def __contains__(self, key):
        return self._items.__contains__(key)

    def keys(self):
        return self._items.keys()

    def items(self):
        return self._items.items()

    def values(self):
        return self._items.values()

    def recycle(self, key, value):
        self._recycle_bin[key] = value

    def unrecycle(self, *args, **kwargs):
        return self._recycle_bin.pop(*args, **kwargs)

    def get(self, *args, **kwargs):
        return (self._recycle_bin.get(*args, **kwargs)
                or self._items.get(*args, **kwargs))

    def pop(self, *args, **kwargs):
        return self._items.pop(*args, **kwargs)

    def popitem(self, *args, **kwargs):
        self._items.popitem(*args, **kwargs)

    def append(self, data: dict):
        raise NotImplementedError

    def extend(self, data):
        return [self.append(d) for d in data]


class BaseSubState(_StateCommon):
    def __init__(self, *, superstate):
        self.superstate = superstate
        self._keys = set()

    def add_key(self, key):
        self._keys.add(key)

    def set_keys(self, keys):
        self._keys = set(keys)

    def remove_key(self, key):
        self._keys.remove(key)

    def __key_for__(self, item):
        raise NotImplementedError

    def __repr__(self):
        return f'<{self.__class__.__name__} length={len(self)}>'

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        for key in self._keys.copy():
            try:
                yield self.superstate[key]
            except KeyError:
                self.remove_key(key)

    def __reversed__(self):
        for key in reversed(self._keys.copy()):
            try:
                yield self.superstate[key]
            except KeyError:
                self.remove_key(key)

    def __getitem__(self, key):
        item = self.superstate.__getitem__(key)
        if self.__key_for__(item) not in self._keys:
            raise KeyError(key)
        return item

    def get(self, key, default=None):
        item = self.superstate.get(key, default)
        if self.__key_for__(item) not in self._keys:
            return default
        return item
