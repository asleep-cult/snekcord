from datetime import datetime

from ..exceptions import PartialObjectError
from ..templates import BaseTemplate
from ..utils import JsonObject


class BaseObject(JsonObject, template=BaseTemplate):
    __slots__ = ('_state', 'id', 'cached', 'deleted', 'deleted_at')

    def __init__(self, *, state):
        self._state = state
        self.id = None
        self.cached = False
        self.deleted = False
        self.deleted_at = None

    def __hash__(self):
        if self.id is None:
            raise PartialObjectError(f'{self.__class__.__name__} object is '
                                     'missing a proper id and therefore is '
                                     'unhashable')
        return hash(self.id)

    def __repr__(self):
        return (f'{self.__class__.__name__}(id={self.id}, '
                f'cached={self.cached}, deleted={self.deleted})')

    def _delete(self):
        self.deleted = True
        self.deleted_at = datetime.now()
        self.uncache()

    def cache(self):
        self.cached = self._state.set(self.id, self)
        if self.cached:
            self._state.unrecycle(self.id, None)

    def uncache(self):
        self.cached = False
        self._state.pop(self.id, None)
        self._state.recycle(self.id, self)

    async def fetch(self):
        return await self._state.fetch(self.id)
