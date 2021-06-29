from .baseobject import BaseObject
from ..enums import PremiumType
from ..flags import UserFlags
from ..utils.json import JsonField

__all__ = ('User',)


class User(BaseObject):
    name = JsonField('username')
    discriminator = JsonField('discriminator')
    avatar = JsonField('avatar')
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
        return f'@{self.name}'

    @property
    def tag(self):
        return f'{self.name}#{self.id}'

    @property
    def mention(self):
        return f'<@{self.id}>'
