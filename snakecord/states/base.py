from __future__ import annotations

from ..utils.snowflake import Snowflake


class Mapping(dict):
    def __iter__(self):
        return iter(list(self.values()))

    def __reversed__(self):
        return reversed(list(self.items()))


class SnowflakeMapping(Mapping):
    def __setitem__(self, key, value):
        return super().__setitem__(Snowflake.try_snowflake(key), value)

    def __getitem__(self, key):
        return super().__getitem__(Snowflake.try_snowflake(key))

    def __delitem__(self, key):
        return super().__delattr__(Snowflake.try_snowflake(key))

    def __contains__(self, key) -> bool:
        return super().__contains__(Snowflake.try_snowflake(key))

    def get(self, key, default=None):
        return super().get(Snowflake.try_snowflake(key), default)

    def pop(self, key, *args, **kwargs):
        return super().pop(Snowflake.try_snowflake(key), *args, **kwargs)


class BaseState:
    __container__ = Mapping
    __maxsize__ = 0

    def __init__(self, *, manager) -> None:
        self._items = self.__container__()
        self.manager = manager

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, length={len(self)}>'

    @classmethod
    def set_maxsize(cls, maxsize: int) -> None:
        cls.__maxsize__ = maxsize

    @classmethod
    def get_maxsize(cls) -> int:
        return cls.__maxsize__

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return self._items.__iter__()

    def __reversed__(self):
        return self._items.__reversed__()

    def __setitem__(self, key, value):
        if self.__maxsize__ != 0 and len(self) >= self.__maxsize__:
            key = next(iter(reversed(self._items.keys())))
            del self._items[key]
        self._items.__setitem__(key, value)

    def __getitem__(self, key):
        return self._items.__getitem__(key)

    def __delitem__(self, key):
        return self._items.__delitem__(key)

    def __contains__(self, key):
        return self._items.__contains__(key)

    def get(self, *args, **kwargs):
        return self._items.get(*args, **kwargs)

    def pop(self, *args, **kwargs):
        return self._items.pop(*args, **kwargs)

    def find(self, func):
        for item in self:
            if func(item):
                return item

    def append(self, data: dict):
        raise NotImplementedError


class BaseSubState:
    def __init__(self, *, superstate: BaseState) -> None:
        self.superstate = superstate

    __repr__ = BaseState.__repr__

    def __related__(self, item) -> bool:
        raise NotImplementedError

    def __len__(self):
        return sum(1 for _ in self)

    def __iter__(self):
        for item in self.superstate:
            if self.__related__(item):
                yield item

    def __reversed__(self):
        for item in reversed(self.superstate):
            if self.__related__(item):
                yield item

    def __getitem__(self, key):
        item = self.superstate.__getitem__(key)
        if not self.__related__(item):
            raise KeyError(key)
        return item

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True

    def get(self, key, default=None):
        item = self.superstate.get(key, default)
        if not self.__related__(item):
            return default
        return item

    find = BaseState.find
