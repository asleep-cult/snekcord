from .. import json
from ..snowflake import Snowflake

__all__ = ('BaseModel', 'ModelWrapper')


class _IDField(json.JSONField):
    def __init__(self) -> None:
        super().__init__('id', repr=True)

    def construct(self, value: str) -> Snowflake:
        return Snowflake(value)

    def deconstruct(self, value: Snowflake) -> str:
        return str(value)


class _ModelMixin:
    __slots__ = ()

    def __init__(self, *, state) -> None:
        self.state = state

    def _get_id(self):
        raise NotImplementedError

    @property
    def client(self):
        return self.state.client

    def is_cached(self) -> bool:
        return self.id in self.state.keys()

    async def fetch(self):
        return await self.state.fetch(self.id)


class BaseModel(json.JSONObject, _ModelMixin):
    __slots__ = ('__weakref__', 'state')

    id = _IDField()

    def __init__(self, *, state) -> None:
        super().__init__(state=state)
        self.state.cache[self.id] = self

    def _get_id(self):
        return self.id


class ModelWrapper(_ModelMixin):
    """A wrapper for an object that might not be cached.

    state: The state that the wrapped object belongs to.

    id: The id of the wrapped object.
    """

    __slots__ = ('__weakref__', 'state', 'id')

    def __init__(self, *, state, id) -> None:
        super().__init__(state=state)
        self.set_id(id)

    def __repr__(self) -> str:
        return f'<ModelWrapper id={self.id}>'

    def _get_id(self):
        return self.id

    def set_id(self, id):
        """Changes the id of the wrapper."""
        if id is not None:
            self.id = self.state.unwrap_id(id)
        else:
            self.id = None

    def unwrap(self):
        """Eqivalent to `self.state.get(self.id)`."""
        return self.state.get(self.id)
