from .baseobject import BaseObject, BaseTemplate
from ..utils import Enum, Flag, JsonField, JsonTemplate, NamedBitset

__all__ = ('User',)


class UserFlags(NamedBitset):
    DISCORD_EMPLOYEE = Flag(0)
    PARTNERED_SERVER_OWNER = Flag(1)
    HYPESQUAD_EVENTS = Flag(2)
    BUG_HUNTER_LEVEL_1 = Flag(3)
    MFA_SMS = Flag(4)
    PREMIUM_PROMO_DISMISSED = Flag(5)
    HOUSE_BRAVERY = Flag(6)
    HOUSE_BRILLIANCE = Flag(7)
    HOUSE_BALANCE = Flag(8)
    EARLY_SUPPORTER = Flag(9)
    TEAM_USER = Flag(10)
    HAS_UNREAD_URGENT_MESSAGES = Flag(13)
    BUG_HUNTER_LEVEL_2 = Flag(14)
    VERIFIED_BOT = Flag(16)
    EARLT_VERIFIED_BOT_DEVELOPER = Flag(17)
    DISCORD_CERTIFIED_MODERATOR = Flag(18)


class PermiumType(Enum, type=int):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2


UserTemplate = JsonTemplate(
    name=JsonField('username'),
    discriminator=JsonField('discriminator'),
    avatar=JsonField('avatar'),
    bot=JsonField('bot'),
    system=JsonField('system'),
    mfa_enabled=JsonField('mfa_enabled'),
    locale=JsonField('locale'),
    verified=JsonField('verified'),
    email=JsonField('email'),
    flags=JsonField(
        'flags',
        UserFlags.from_value,
        UserFlags.get_value
    ),
    premium_type=JsonField(
        'premium_type',
        PermiumType.get_enum,
        PermiumType.get_value
    ),
    public_flags=JsonField(
        'public_flags',
        UserFlags.from_value,
        UserFlags.get_value
    ),
    __extends__=(BaseTemplate,)
)


class User(BaseObject, template=UserTemplate):
    def __str__(self):
        return f'@{self.name}'

    @property
    def tag(self):
        return f'{self.name}#{self.id}'

    @property
    def mention(self):
        return f'<@{self.id}>'
