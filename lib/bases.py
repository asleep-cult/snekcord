from .utils import (
    Snowflake,
    JsonStructure,
    JsonField,
    _try_snowflake
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class BaseState:
    def __init__(self, client):
        self._client: 'Client' = client
        self._values = {}

    def __iter__(self):
        return iter(self._values.values())

    def __len__(self):
        return len(self._values)

    def __getitem__(self, item):
        item = _try_snowflake(item)
        return self._values[item]

    def __delitem__(self, item):
        item = _try_snowflake(item)
        del self._values[item]

    def __contains__(self, item):
        try:
            self[item]
        except KeyError:
            return False
        return True

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._values)

    def get(self, item, default=None):
        try:
            value = self[item]
        except KeyError:
            return default
        return value

    def pop(self, item):
        item = _try_snowflake(item)
        return self._values.pop(item)

    def clear(self):
        self._values = {}

    def _add(self, *args, **kwargs):
        raise NotImplementedError

    async def fetch(self, object_id):
        raise NotImplementedError


class BaseObject(JsonStructure):
    __json_fields__ = {
        'id': JsonField('id', Snowflake, str)
    }

    id: Snowflake
    _state: BaseState

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.__json_fields__['id'] = JsonField('id', Snowflake, str)

    def set_class(self, cls):
        self.__state_class__ = cls

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.id == self.id
