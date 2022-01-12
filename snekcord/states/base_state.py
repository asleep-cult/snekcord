from ..collection import Collection
from ..objects import ObjectWrapper

__all__ = ('BaseSate',)


class BaseSate:
    """The base class for all states. Represents the cache and state-specific
    functionality for a specific object e.g. `fetch`, `create`.

    client:
        The client that the state belongs to.

    cache:
        The underlying Collection that holds the objects instanciated by the state.
    """

    def __init__(self, *, client) -> None:
        self.client = client
        self.cache = Collection()

    def __contains__(self, object) -> bool:
        return self.unwrap_id(object) in self.cache.keys()

    def __iter__(self):
        return iter(self.cache)

    def wrap_id(self, object):
        """Creates a ObjectWrapper for a specific object."""
        return ObjectWrapper(state=self, id=object)

    @classmethod
    def unwrap_id(cls, object):
        raise NotImplementedError

    def get(self, object):
        """Retrieves the object with the corresponding id from the state's cache.

        Raises:
            CacheLookupError: The object does not exist in the state's cache.
        """
        return self.cache.get(self.unwrap_id(object))

    def pop(self, object):
        return self.cache.pop(self.unwrap_id(object))

    async def upsert(self, data):
        raise NotImplementedError

    async def fetch(self, object):
        raise NotImplementedError
