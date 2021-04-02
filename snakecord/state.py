from .utils import _try_snowflake, undefined
from .client import Client

class BaseState:
    _maxsize = None

    def __init__(self, *, client: Client):
        self.client = client
        self._items = {}

    def __iter__(self):
        return iter(list(self._items.values()))

    def __len__(self):
        return len(self._items)

    def __getitem__(self, item):
        item = _try_snowflake(item)
        return self._items[item]

    def __delitem__(self, item):
        item = _try_snowflake(item)
        del self._items[item]

    def __contains__(self, item):
        item = _try_snowflake(item)
        return item in self._items

    def __reversed__(self):
        return reversed(list(self._items.values()))

    def __repr__(self):
        return '<{} length={}>'.format(self.__class__.__qualname__, len(self))

    def get(self, item, default=None):
        item = _try_snowflake(item)
        return self._items.get(item, default)

    def pop(self, item, default=undefined):
        item = _try_snowflake(item)
        item = self._items.pop(item, default)
        if item is undefined:
            raise KeyError(item)
        return item

    def clear(self):
        self._items.clear()

    def find(self, func):
        for item in self:
            if func(item):
                return item

    def _check_size(self):
        if len(self) >= self._maxsize:
            last = next(iter(reversed(self._items)))
            self.pop(last)

    def append(self, *args, **kwargs):
        raise NotImplementedError

    async def fetch(self, object_id):
        raise NotImplementedError

    @classmethod
    def set_maxsize(cls, maxsize):
        cls._maxsize = maxsize


class BaseSubState:
    def __init__(self, *, superstate):
        self.superstate = superstate

    def _check_relation(self, obj):
        raise NotImplementedError

    def __iter__(self):
        for item in self.superstate:
            if self._check_relation(item):
                yield item

    def __len__(self):
        i = 0
        for _ in self:
            i += 1
        return i

    def __getitem__(self, item):
        item = self.superstate[item]
        if not self._check_relation(item):
            raise KeyError(item)
        return item

    def __contains__(self, item):
        return self._check_relation(self.get(item))

    def __reversed__(self):
        for item in reversed(self.superstate):
            if self._check_relation(item):
                yield item

    __repr__ = BaseState.__repr__

    def get(self, item, default=None):
        item = self.superstate.get(item, default)
        if not self._check_relation(item):
            return default
        return item

    def pop(self, item, default=undefined):
        raise NotImplementedError

    def find(self, func):
        for item in self:
            if func(item):
                return item
