from datetime import datetime

from ..exceptions import PartialObjectError
from ..utils.json import JsonField, JsonObject, JsonTemplate
from ..utils.snowflake import Snowflake

__all__ = ('BaseObject',)

BaseTemplate = JsonTemplate(
    id=JsonField('id', Snowflake, str),
)


class BaseObject(JsonObject, template=BaseTemplate):
    """The base class for all cachable Discord entities

    Attributes:
        state BaseState: The state that the object belongs to

        id Optional[Snowflake|str]: The object's unique identifier
            provided by Discord's API, the will be the object's `code`
            for `GuildTemplate` and `Invite` objects

        cached bool: Whether or not the object is stored in its state's cache

        deleted bool: Whether or not the object is deleted

        deleted_at Optional[datetime]: The time at which the object was
            marked as deleted

    warning:
        The `deleted` and `deleted_at` attributes will only be accurate
        for objects maintained by a Discord WebSocket connection
    """
    __slots__ = ('state', 'id', 'cached', 'deleted', 'deleted_at',
                 '__weakref__')

    def __init__(self, *, state):
        self.state = state
        self.cached = False
        self.deleted = False
        self.deleted_at = None

    def __hash__(self):
        """Equivalent to `hash(self.id)`

        Raises:
            PartialObjectError: Raised when the object's id is None
        """
        if self.id is None:
            raise PartialObjectError(
                f'{self.__class__.__name__} object is missing a valid id')
        return hash(self.id)

    def __repr__(self):
        return (f'<{self.__class__.__name__} id={self.id!r},'
                f' cached={self.cached}, deleted={self.deleted}>')

    def _delete(self):
        self.deleted = True
        self.deleted_at = datetime.now()
        self.uncache(recycle=False)

    def cache(self):
        """Stores the object in the state's cache"""
        self.cached = True
        self.state[self.id] = self

    def uncache(self):
        """Removes the object from the state's cache"""
        self.cached = False
        self.state.pop(self.id, None)

    async def fetch(self):
        """Equivalent to `self.state.fetch(self.id)`"""
        return await self.state.fetch(self.id)
