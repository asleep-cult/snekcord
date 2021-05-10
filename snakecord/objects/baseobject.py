from ..templates import BaseTemplate
from ..utils import JsonObject


class BaseObject(JsonObject, template=BaseTemplate):
    def __init__(self, *, state):
        self._state = state
        self.id = None
        self.cached = False
        self.deleted = False

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return (f'<{self.__class__.__name__} id={self.id},'
                f' cached={self.cached}, deleted={self.deleted}>')

    def _delete(self):
        self.deleted = True
        self.uncache()

    def cache(self):
        self.cached = self._state.set(self.id, self)
        if self.cached:
            self._state.unrecycle(self.id, None)

    def uncache(self):
        self.cached = False
        self._state.pop(self.id, None)
        self._state.recycle(self.id, self)
