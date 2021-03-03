from .bases import BaseObject, BaseState
from .utils import JsonField, Snowflake

from typing import Optional


class User(BaseObject):
    __slots__ = (
        '_state', 'name', 'discriminator', 'avatar', 'bot', 'system',
        'mfa_enabled', 'locale', 'verified', 'email', 'flags',
        'premium_type', 'public_flags'
    )

    __json_fields__ = {
        'name': JsonField('username'),
        'discriminator': JsonField('discriminator'),
        'avatar': JsonField('avatar'),
        'bot': JsonField('bot'),
        'system': JsonField('system'),
        'mfa_enabled': JsonField('mfa_enabled'),
        'locale': JsonField('locale'),
        'verified': JsonField('verified'),
        'email': JsonField('email'),
        'flags': JsonField('flags'),
        'premium_type': JsonField('premium_type'),
        'public_flags': JsonField('public_flags'),
    }

    id: Snowflake
    name: str
    discriminator: int
    avatar: str
    bot: Optional[bool]
    system: Optional[bool]
    mfa_enabled: Optional[bool]
    locale: Optional[str]
    verified: Optional[bool]
    email: Optional[str]
    flags: Optional[int]
    premium_type: Optional[int]
    public_flags: Optional[int]

    def __init__(self, *, state):
        self._state = state


class UserState(BaseState):
    __state_class__ = User

    def _add(self, data) -> User:
        user = self.get(data['id'])
        if user is not None:
            user._update(data)
            return user
        user = self.__state_class__.unmarshal(data, state=self)
        self._values[user.id] = user
        self._client.events.user_cache(user)
        return user

    async def fetch(self, user_id) -> User:
        data = await self._client.rest.get_user(user_id)
        return self._add(data)
