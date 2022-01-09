from ..collection import Collection
from ..exceptions import UnknownModelError
from ..models import ModelWrapper

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
        """Creates a ModelWrapper for a specific object."""
        return ModelWrapper(state=self, id=object)

    @classmethod
    def unwrap_id(cls, object):
        raise NotImplementedError

    def get(self, object):
        """Retrieves the object with the corresponding id from the state's cache.

        Raises:
            CacheLookupError: The object does not exist in the state's cache.
        """
        id = self.unwrap_id(object)

        model = self.cache.get(id)
        if model is None:
            raise UnknownModelError(id) from None

        return model

    def pop(self, object):
        id = self.unwrap_id(object)

        model = self.cache.pop(id, None)
        if model is None:
            raise UnknownModelError(id)

        return model

    async def upsert(self, data):
        raise NotImplementedError

    async def fetch(self, object):
        raise NotImplementedError
