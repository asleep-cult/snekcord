from datetime import datetime

from ..exceptions import PartialObjectError
from ..utils import JsonField, JsonObject, JsonTemplate, Snowflake

__all__ = ('BaseObject',)

BaseTemplate = JsonTemplate(
    id=JsonField('id', Snowflake, str),
)


class BaseObject(JsonObject, template=BaseTemplate):
    __slots__ = ('state', 'id', 'cached', 'deleted', 'deleted_at')

    def __json_init__(self, *, state):
        self.state = state
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
        return (f'{self.__class__.__name__}(id={self.id!r}, '
                f'cached={self.cached}, deleted={self.deleted})')

    def _delete(self):
        self.deleted = True
        self.deleted_at = datetime.now()
        self.uncache(recycle=False)

    def cache(self):
        self.cached = self.state.set(self.id, self)
        if self.cached:
            self.state.unrecycle(self.id, None)

    def uncache(self, recycle=True):
        self.cached = False
        self.state.pop(self.id, None)
        if recycle:
            self.state.recycle(self.id, self)

    async def fetch(self):
        return await self.state.fetch(self.id)
