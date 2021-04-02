from . import structures
from .state import BaseState


class User(structures.User):
    __slots__ = (
        '_state',
    )

    def __init__(self, *, state):
        self._state = state


class UserState(BaseState):
    def append(self, data) -> User:
        user = self.get(data['id'])
        if user is not None:
            user._update(data)
            return user

        user = User.unmarshal(data, state=self)
        self._items[user.id] = user
        return user

    async def fetch(self, user_id) -> User:
        rest = self.client.rest
        data = await rest.get_user(user_id)
        return self.append(data)
