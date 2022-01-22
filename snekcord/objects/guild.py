import enum

import attr

from .base import SerializedObject, SnowflakeObject
from .. import json

__all__ = (
    'GuildMessageNotificationsLevel',
    'GuildMFALevel',
    'GuildVerificationLevel',
    'GuildNSFWLevel',
    'GuildExplicitContentFilter',
    'GuildPremiumTier',
    'GuildSystemChannelFlags',
    'Guild',
)


class GuildMessageNotificationsLevel(enum.IntEnum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class GuildMFALevel(enum.IntEnum):
    NONE = 0
    ELEVATED = 1


class GuildVerificationLevel(enum.IntEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class GuildNSFWLevel(enum.IntEnum):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class GuildExplicitContentFilter(enum.IntEnum):
    DISABLED = 0
    MEMBERS_WITH_ROLES = 1
    ALL_MEMBERS = 2


class GuildPremiumTier(enum.IntEnum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class GuildSystemChannelFlags(enum.IntFlag):
    SUPPRESS_JOIN_NOTIFICATIONS = 1 << 0
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1 << 1
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = 1 << 2
    SUPPRESS_JOIN_NOTIFICATION_REPLIES = 1 << 3


class GuildFeature(enum.Enum):
    ANIMATED_ICON = 'ANIMATED_ICON'
    BANNER = 'BANNER'
    COMMERCE = 'COMMERCE'
    COMMUNITY = 'COMMUNITY'
    DISCOVERABLE = 'DISCOVERABLE'
    FEATURABLE = 'FEATURABLE'
    INVITE_SPLASH = 'INVITE_SPLASH'
    MEMBER_VERIFICATION_GATE_ENABLED = 'MEMBER_VERIFICATION_GATE_ENABLED'
    MONETIZATION_ENABLED = 'MONETIZATION_ENABLED'
    MORE_STICKERS = 'MORE_STICKERS'
    NEWS = 'NEWS'
    PARTNERED = 'PARTNERED'
    PREVIEW_ENABLED = 'PREFIEW_ENABLED'
    PRIVATE_THREADS = 'PRIVATE_THREADS'
    ROLE_ICONS = 'ROLE_ICONS'
    SEVEN_DAY_THREAD_ARCHIVE = 'SEVEN_DAY_THREAD_ARCHIVE'
    THREE_DAY_THREAD_ARCHIVE = 'THREE_DAY_THREAD_ARCHIVE'
    TICKETED_EVENTS_ENABLED = 'TICKETED_EVENTS_ENABLED'
    VANITY_URL = 'VANITY_URL'
    VERIFIED = 'VERIFIED'
    VIP_REGIONS = 'VIP_REGIONS'
    WELCOME_SCREEN_ENABLED = 'WELCOME_SCREEN_ENABLED'


class SerializedGuild(SerializedObject):
    name = json.JSONField('name')
    icon = json.JSONField('icon')
    splash = json.JSONField('splash')
    discovery_splash = json.JSONField('discovery_splash')
    afk_timeout = json.JSONField('afk_timeout')
    features = json.JSONArray('features')
    system_channel_flags = json.JSONField('system_channel_flags')
    verification_level = json.JSONField('verification_level')
    message_notifications_level = json.JSONField('default_message_notifications')
    explicit_content_filter = json.JSONField('explicit_content_filter')
    mfa_level = json.JSONField('mfa_level')
    nsfw_level = json.JSONField('nsfw_level')
    premium_tier = json.JSONField('premium_tier')
    large = json.JSONField('large')
    unavailable = json.JSONField('unavailable')
    max_presences = json.JSONField('max_presences')
    max_members = json.JSONField('max_members')
    description = json.JSONField('description')
    preferred_locale = json.JSONField('preferred_locale')
    role_ids = json.JSONArray('role_ids')
    emoji_ids = json.JSONArray('emoji_ids')
    member_ids = json.JSONArray('member_ids')
    channel_ids = json.JSONArray('channel_ids')


@attr.s(kw_only=True)
class Guild(SnowflakeObject):
    name: str = attr.ib()
    icon: str = attr.ib()
    splash: str = attr.ib()
    discovery_splash: str = attr.ib()
    afk_timeout: int = attr.ib()
    features: list[GuildFeature] = attr.ib()
    system_channel_flags: GuildSystemChannelFlags = attr.ib()
    verification_level: GuildVerificationLevel = attr.ib()
    message_notifications_level: GuildMessageNotificationsLevel = attr.ib()
    explicit_content_filter: GuildExplicitContentFilter = attr.ib()
    mfa_level: GuildMFALevel = attr.ib()
    nsfw_level: GuildNSFWLevel = attr.ib()
    premium_tier: GuildPremiumTier = attr.ib()
    large: bool = attr.ib()
    unavailable: bool = attr.ib()
    max_presences: int = attr.ib()
    max_members: int = attr.ib()
    description: str = attr.ib()
    preferred_locale: str = attr.ib()
    roles = attr.ib()
    emojis = attr.ib()
    members = attr.ib()
    channels = attr.ib()
