import typing as t

if t.TYPE_CHECKING:
    from .channel import DMChannel

from . import structures
from .state import BaseState


class User(structures.User):
    __slots__ = (
        '_state', 'dm_channel'
    )

    def __init__(self, *, state: 'UserState'):
        self._state = state
        self.dm_channel: t.Optional['DMChannel'] = None


class UserState(BaseState):
    def append(self, data: dict) -> User:
        user = self.get(data['id'])
        if user is not None:
            user._update(data)
            return user

        user = User.unmarshal(data, state=self)
        self._items[user.id] = user
        return user

    async def fetch(self, user_id: int) -> User:
        rest = self.client.rest
        data = await rest.get_user(user_id)
        return self.append(data)
