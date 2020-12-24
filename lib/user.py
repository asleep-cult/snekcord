from .bases import (
    BaseObject, 
    BaseState
)

from .utils import (
    JsonField
)


class User(BaseObject):
    __json_slots__ = (
        '_state', 'name', 'discriminator', 'avatar', 'bot', 'system', 
        'mfa_enabled', 'locale', 'verified', 'email', 'flags', 
        'premium_type', 'public_flags'
    )

    name: str = JsonField('username')
    discriminator: int = JsonField('discriminator')
    avatar: str = JsonField('avatar')
    bot: bool = JsonField('bot')
    system: bool = JsonField('system')
    mfa_enabled: bool = JsonField('mfa_enabled')
    locale: str = JsonField('locale')
    verified: bool = JsonField('verified')
    email: str = JsonField('email')
    flags: int = JsonField('flags')
    premium_type: int = JsonField('premium_type')
    public_flags: int = JsonField('public_flags')

    def __init__(self, *, state):
        self._state = state

    def _update(self, *args, **kwargs):
        pass


class UserState(BaseState):
    async def fetch(self, user_id) -> User:
        data = await self._client.rest.get_user(user_id)
        return self._add(data)

    def _add(self, data) -> User:
        user = self.get(data['id'])
        if user is not None:
            user._update(data)
            return user
        user = User.unmarshal(data, state=self)
        self._values[user.id] = user
        return user
