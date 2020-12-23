from .utils import (
    Snowflake,
    JsonStructure,
    JsonField,
    _try_snowflake
)


class BaseState:
    def __init__(self, client):
        self._client = client
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
        return self._values.pop(_try_snowflake(item))

    def clear(self):
        self._values = {}

    def add(self, *args, **kwargs):
        raise NotImplementedError

    async def fetch(self, object_id):
        raise NotImplementedError


class BaseObject(JsonStructure):
    __json_slots__ = ('id',)

    id: Snowflake = JsonField('id', Snowflake, str)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.id == self.id