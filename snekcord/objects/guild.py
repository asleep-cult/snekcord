from __future__ import annotations

import enum
import typing
from datetime import datetime

import attr

from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined
from .base import SnowflakeObject

if typing.TYPE_CHECKING:
    from ..states import (
        ChannelIDWrapper,
        GuildChannelsView,
        GuildEmojisView,
        GuildMembersView,
        GuildRolesView,
        UserIDWrapper,
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
    'GuildFeature',
    'PartialGuild',
    'GuildPreview',
    'Guild',
    'RESTGuild',
)


class CachedGuild(CachedModel):
    """Represents a raw guild within the guild cache."""

    id: Snowflake
    name: str
    icon: typing.Optional[str]
    splash: typing.Optional[str]
    discovery_splash: typing.Optional[str]
    owner_id: str
    afk_channel_id: typing.Optional[str]
    afk_timeout: int
    widget_enabled: MaybeUndefined[bool]
    widget_channel_id: MaybeUndefined[typing.Optional[str]]
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    features: typing.List[str]
    mfa_level: int
    application_id: typing.Optional[str]
    system_channel_id: typing.Optional[str]
    system_channel_flags: int
    rules_channel_id: typing.Optional[int]
    joined_at: MaybeUndefined[str]
    max_presences: MaybeUndefined[int]
    max_members: MaybeUndefined[int]
    vanity_url_code: typing.Optional[str]
    description: typing.Optional[str]
    banner: typing.Optional[str]
    premium_tier: int
    premium_subscription_count: MaybeUndefined[int]
    preferred_locale: str
    public_updates_channel_id: typing.Optional[str]
    max_video_channel_users: MaybeUndefined[int]
    nsfw_level: int


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
    icon: typing.Optional[str] = attr.ib()


class GuildPreview(PartialGuild):
    splash: typing.Optional[str] = attr.ib()
    discovery_splash: typing.Optional[str] = attr.ib()
    features: typing.List[GuildFeature] = attr.ib()
    presence_count: int = attr.ib()
    member_count: int = attr.ib()
    description: str = attr.ib()
    emojis = attr.ib()


@attr.s(kw_only=True)
class Guild(PartialGuild):
    splash: typing.Optional[str] = attr.ib()
    discovery_splash: typing.Optional[str] = attr.ib()
    owner: UserIDWrapper = attr.ib()
    afk_channel: ChannelIDWrapper = attr.ib()
    afk_timeout: int = attr.ib()
    widget_enabled: typing.Optional[bool] = attr.ib()
    widget_channel: ChannelIDWrapper = attr.ib()
    verification_level: typing.Union[GuildVerificationLevel, int] = attr.ib()
    message_notifications_level: typing.Union[GuildMessageNotificationsLevel, int] = attr.ib()
    explicit_content_filter: typing.Union[GuildExplicitContentFilter, int] = attr.ib()
    features: typing.List[typing.Union[GuildFeature, str]] = attr.ib()
    mfa_level: typing.Union[GuildMFALevel, int] = attr.ib()
    # application: ApplicationIDWrapper = attr.ib()
    system_channel: ChannelIDWrapper = attr.ib()
    system_channel_flags: GuildSystemChannelFlags = attr.ib()
    joined_at: typing.Optional[datetime] = attr.ib()
    max_presences: typing.Optional[int] = attr.ib()
    max_members: typing.Optional[int] = attr.ib()
    vanity_url_code: typing.Optional[str] = attr.ib()
    description: typing.Optional[str] = attr.ib()
    banner: typing.Optional[str] = attr.ib()
    premium_tier: typing.Union[GuildPremiumTier, int] = attr.ib()
    premium_subscription_count: typing.Optional[int] = attr.ib()
    preferred_locale: str = attr.ib()
    public_updates_channel: ChannelIDWrapper = attr.ib()
    max_video_channel_users: typing.Optional[int] = attr.ib()
    nsfw_level: typing.Union[GuildNSFWLevel, int] = attr.ib()
    roles: GuildRolesView = attr.ib()
    emojis: GuildEmojisView = attr.ib()
    members: GuildMembersView = attr.ib()
    channels: GuildChannelsView = attr.ib()


@attr.s(kw_only=True)
class RESTGuild(Guild):
    presence_count: typing.Optional[int] = attr.ib()
    member_count: typing.Optional[int] = attr.ib()

    @classmethod
    def from_guild(
        cls,
        guild: Guild,
        *,
        presence_count: typing.Optional[int],
        member_count: typing.Optional[int],
    ) -> RESTGuild:
        return cls(presence_count=presence_count, member_count=member_count, **attr.asdict(guild))
