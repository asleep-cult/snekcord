import enum
from datetime import datetime
from typing import TYPE_CHECKING

import attr

from .base import (
    CachedObject,
    SnowflakeObject,
)
from .. import json
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from ..states import (
        ChannelStateView,
        EmojiStateView,
        MemberStateView,
        RoleStateView,
    )

__all__ = (
    'CachedGuild',
    'GuildMessageNotificationsLevel',
    'GuildMFALevel',
    'GuildVerificationLevel',
    'GuildNSFWLevel',
    'GuildExplicitContentFilter',
    'GuildPremiumTier',
    'GuildSystemChannelFlags',
    'Guild',
)


class CachedGuild(CachedObject):
    name = json.JSONField('name')
    icon = json.JSONField('icon')
    splash = json.JSONField('splash')
    discovery_splash = json.JSONField('discovery_splash')
    owner_id = json.JSONField('owner_id')
    afk_channel_id = json.JSONField('afk_channel_id')
    afk_timeout = json.JSONField('afk_timeout')
    widget_enabled = json.JSONField('widget_enabled')
    widget_channel_id = json.JSONField('widget_channel_id')
    verification_level = json.JSONField('verification_level')
    message_notifications_level = json.JSONField('default_message_notifications')
    explicit_content_filter = json.JSONField('explicit_content_filter')
    role_ids = json.JSONArray('role_ids')
    emoji_ids = json.JSONArray('emoji_ids')
    features = json.JSONArray('features')
    mfa_level = json.JSONField('mfa_level')
    application_id = json.JSONField('application_id')
    system_channel_id = json.JSONField('system_channel_id')
    system_channel_flags = json.JSONField('system_channel_flags')
    rules_channel_id = json.JSONField('rules_channel_id')
    joined_at = json.JSONField('joined_at')
    large = json.JSONField('large')
    unavailable = json.JSONField('unavailable')
    member_count = json.JSONField('member_count')
    voice_state_ids = json.JSONArray('voice_state_ids')
    member_ids = json.JSONArray('member_ids')
    channel_ids = json.JSONArray('channel_ids')
    thread_ids = json.JSONArray('thread_ids')
    max_presences = json.JSONField('max_presences')
    max_members = json.JSONField('max_members')
    vanity_url_code = json.JSONField('vanity_url_code')
    description = json.JSONField('description')
    banner = json.JSONField('banner')
    premium_tier = json.JSONField('premium_tier')
    premium_subscription_count = json.JSONField('premium_subscription_count')
    preferred_locale = json.JSONField('preferred_locale')
    public_updates_channel_id = json.JSONField('public_updates_channel_id')
    max_video_channel_users = json.JSONField('max_video_channel_users')
    nsfw_level = json.JSONField('nsfw_level')


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


@attr.s(kw_only=True)
class PartialGuild(SnowflakeObject):
    name: str = attr.ib()
    icon: str = attr.ib()


class GuildPreview(PartialGuild):
    splash: str = attr.ib()
    discovery_splash = attr.ib()
    features: list[GuildFeature] = attr.ib()
    presence_count: int = attr.ib()
    member_count: int = attr.ib()
    description: str = attr.ib()
    emojis = attr.ib()


class _GuildFields:
    splash: str = attr.ib()
    discovery_splash: str = attr.ib()
    owner_id: Snowflake = attr.ib()
    afk_channel_id: Snowflake = attr.ib()
    afk_timeout: int = attr.ib()
    widget_enabled: bool = attr.ib()
    widget_channel_id: Snowflake = attr.ib()
    verification_level: GuildVerificationLevel = attr.ib()
    message_notifications_level: GuildMessageNotificationsLevel = attr.ib()
    explicit_content_filter: GuildExplicitContentFilter = attr.ib()
    features: list[GuildFeature] = attr.ib()
    mfa_level: GuildMFALevel = attr.ib()
    application_id: Snowflake = attr.ib()
    system_channel_id: Snowflake = attr.ib()
    system_channel_flags: GuildSystemChannelFlags = attr.ib()
    joined_at: datetime = attr.ib()
    max_presences: int = attr.ib()
    max_members: int = attr.ib()
    vanity_url_code: str = attr.ib()
    description: str = attr.ib()
    banner: str = attr.ib()
    premium_tier: GuildPremiumTier = attr.ib()
    premium_subscription_count: int = attr.ib()
    preferred_locale: str = attr.ib()
    public_updates_channel_id: Snowflake = attr.ib()
    max_video_channel_users: int = attr.ib()
    nsfw_level: GuildNSFWLevel = attr.ib()
    roles: RoleStateView = attr.ib()
    emojis: EmojiStateView = attr.ib()


@attr.s(kw_only=True)
class RESTGuild(_GuildFields):
    presence_count: int = attr.ib()
    member_count: int = attr.ib()


@attr.s(kw_only=True)
class Guild(_GuildFields):
    members: MemberStateView = attr.ib()
    channels: ChannelStateView = attr.ib()
