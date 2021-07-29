from .baseobject import BaseObject
from ..enums import PremiumType
from ..fetchables import DefaultUserAvatar, UserAvatar
from ..flags import UserFlags
from ..utils import JsonField

__all__ = ('User',)


class User(BaseObject):
    name = JsonField('username')
    discriminator = JsonField('discriminator')
    bot = JsonField('bot')
    system = JsonField('system')
    mfa_enabled = JsonField('mfa_enabled')
    locale = JsonField('locale')
    verified = JsonField('verified')
    email = JsonField('email')
    flags = JsonField('flags', UserFlags.from_value)
    premium_type = JsonField('premium_type', PremiumType.get_enum)
    public_flags = JsonField('public_flags', UserFlags.from_value)

    def __str__(self):
        return f'@\u200b{self.name}'  # Escape it just in case their name is 'everyone'

    @property
    def tag(self):
        return f'{self.name}#{self.id}'

    @property
    def mention(self):
        return f'<@{self.id}>'

    @property
    def avatar(self):
        avatar = self._json_data_.get('avatar')
        if avatar is not None:
            return UserAvatar(self.state.client.rest, self.id, avatar)
        return self.default_avatar

    @property
    def default_avatar(self):
        return DefaultUserAvatar(self.state.client.rest, int(self.discriminator))
