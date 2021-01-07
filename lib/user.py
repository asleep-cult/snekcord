from .bases import (
    BaseObject, 
    BaseState
)

from .utils import (
    JsonField,
    Snowflake
)


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
    bot: bool
    system: bool
    mfa_enabled: bool
    locale: str
    verified: bool
    email: str
    flags: int
    premium_type: int
    public_flags: int

    def __init__(self, *, state):
        self._state = state

    def _update(self, *args, **kwargs):
        pass


class UserState(BaseState):
    def _add(self, data) -> User:
        user = self.get(data['id'])
        if user is not None:
            user._update(data)
            return user
        user = User.unmarshal(data, state=self)
        self._values[user.id] = user
        return user

    async def fetch(self, user_id) -> User:
        data = await self._client.rest.get_user(user_id)
        return self._add(data)
