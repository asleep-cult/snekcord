import enum

from .base_models import BaseModel
from .. import json

__all__ = ('UserFlags', 'PremiumType', 'User')


class UserFlags(enum.IntFlag):
    NONE = 0
    STAFF = 1 << 0
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSUEDO_USER = 1 << 10
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19


class PremiumType(enum.IntEnum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2


class User(BaseModel):
    name = json.JSONField('username')
    discriminator = json.JSONField('discriminator')
    avatar = json.JSONField('avatar')
    bot = json.JSONField('bot')
    system = json.JSONField('system')
    mfa_enabled = json.JSONField('mfa_enabled')
    banner = json.JSONField('banner')
    accent_color = json.JSONField('accent_color')
    locale = json.JSONField('locale')
    verified = json.JSONField('verified')
    email = json.JSONField('email')
    flags = json.JSONField('flags', UserFlags)
    premium_type = json.JSONField('premium_type', PremiumType)
    public_flags = json.JSONField('public_flags', UserFlags)
