from ..utils import JsonField, JsonObject, ReprHelper, Snowflake

__all__ = ('BaseObject',)


class BaseObject(JsonObject, ReprHelper):
    __slots__ = ('state', 'cached', 'deleted', 'deleted_at', '__weakref__')

    _repr_fields_ = ('id', 'cached', 'deleted')

    id = JsonField('id', Snowflake)

    def __init__(self, *, state):
        self.state = state
        self.cached = False
        self.deleted = False

    def __hash__(self):
        return hash(self.id)

    def _delete(self):
        self.deleted = True
        self.uncache()

    def cache(self):
        self.state.mapping[self.id] = self
        self.cached = True

    def uncache(self):
        del self.state.mapping[self.id]
        self.cached = False

    def fetch(self):
        return self.state.fetch(self.id)
