from .utils import (
    JsonStructure,
    JsonField,
    Snowflake
)

class User(JsonStructure):
    id: Snowflake = JsonField('id', Snowflake, str)
    name: str = JsonField('name')
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

class UserState:
    def __init__(self, client):
        self._client = client
        self._users = {}

    def get(self, item, default=None):
        try:
            snowflake = Snowflake(item)
        except ValueError:
            return default
        return self._users.get(snowflake, default)

    def __getitem__(self, item):
        try:
            snowflake = Snowflake(item)
        except ValueError:
            snowflake = item
        return self._users[snowflake]

    def __len__(self):
        return len(self._channels)

    async def fetch(self, user_id):
        data = await self._client.rest.get_user(user_id)
        return self.add(data)

    def add(self, data):
        user = self.get(data['id'])
        if user is not None:
            user._update(data)
            return user
        user = User.unmarshal(data, state=self)
        self._users[user.id] = user
        return user