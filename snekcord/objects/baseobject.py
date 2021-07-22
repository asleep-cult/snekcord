from ..utils import JsonField, JsonObject, ReprHelper, Snowflake

__all__ = ('BaseObject',)


class BaseObject(JsonObject, ReprHelper):
    """The base class for all Discord entities.

    state BaseState: The state that the object belongs to.

    id Optional[Snowflake | str]: The object's unique identifier used
        for caching and interacting with Discord's API.

    cached bool: True if the object is currently stored in its state's
        cache otherwise False.

    deleted bool: True if a delete event has been fired for the object
        otherwise False.
    """
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
        """Stores the object in the state's cache"""
        self.state.mapping[self.id] = self
        self.cached = True

    def uncache(self):
        """Removes the object from the state's cache"""
        del self.state.mapping[self.id]
        self.cached = False

    def fetch(self):
        """Equivalent to `self.state.fetch(self.id)`"""
        return self.state.fetch(self.id)
