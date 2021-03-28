from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client

from .utils import _try_snowflake


class BaseState:
    def __init__(self, client: 'Client'):
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

    def __repr__(self):
        return '{0.__class__.__name__}({0._items})'.format(self)

    def get(self, item, default=None):
        item = _try_snowflake(item)
        return self._items.get(item, default)

    def pop(self, item, *args, **kwargs):
        item = _try_snowflake(item)
        return self._items.pop(item, *args, **kwargs)

    def clear(self):
        self._items.clear()

    def find(self, func):
        for item in self:
            if func(item):
                return item

    def append(self, *args, **kwargs):
        raise NotImplementedError

    async def fetch(self, object_id):
        raise NotImplementedError
