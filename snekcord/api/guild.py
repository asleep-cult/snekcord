from __future__ import annotations

import enum
import typing

from ..enums import convert_enum
from ..snowflake import Snowflake

if typing.TYPE_CHECKING:
    from typing_extensions import NotRequired

    from .channel import RawChannel
    from .emoji import RawCustomEmoji
    from .sticker import RawCustomSticker


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


class RawPartialGuild(typing.TypedDict):
    id: Snowflake
    name: str
    icon: typing.Optional[str]


class RawGuildPreview(RawPartialGuild):
    splash: typing.Optional[str]
    discovery_splash: typing.Optional[str]
    emojis: typing.List[RawCustomEmoji]
    features: typing.List[GuildFeature]
    approximate_member_count: int
    approximate_presence_count: int
    description: str
    stickers: typing.List[RawCustomSticker]


class RawGuild(RawPartialGuild):
    icon_hash: NotRequired[typing.Optional[str]]
    splash: typing.Optional[str]
    discovery_splash: typing.Optional[str]
    owner_id: Snowflake
    afk_channel_id: Snowflake
    afk_timeout: int
    widget_enabled: NotRequired[bool]
    widget_channel_id: NotRequired[typing.Optional[Snowflake]]
    verification_level: typing.Union[GuildVerificationLevel, int]
    default_message_notifications: typing.Union[GuildMessageNotificationsLevel, int]
    explicit_content_filter: typing.Union[GuildExplicitContentFilter, int]
    roles: typing.List[RawRole]
    emojis: typing.List[RawCustomEmoji]
    features: typing.List[GuildFeature]
    mfa_level: typing.Union[GuildMFALevel, int]
    application_id: typing.Optional[Snowflake]
    system_channel_id: typing.Optional[Snowflake]
    system_channel_flags: int
    rules_channel_id: typing.Optional[Snowflake]
    max_presences: NotRequired[typing.Optional[int]]
    max_members: NotRequired[int]
    vanity_url_code: typing.Optional[str]
    description: typing.Optional[str]
    banner: typing.Optional[str]
    premium_tier: typing.Union[GuildPremiumTier, int]
    premium_subscription_count: NotRequired[int]
    preferred_locale: str
    public_updates_channel_id: typing.Optional[Snowflake]
    max_video_channel_users: NotRequired[int]
    nsfw_level: typing.Union[GuildNSFWLevel, int]
    stickers: NotRequired[typing.List[RawCustomSticker]]
    premium_progress_bar_enabled: bool


class RawCurrentUserGuild(RawGuild):
    owner: bool
    permissions: int


class RawGuildWithCounts(RawGuild):
    approximate_member_count: int
    approximate_presence_count: int


class RawInviteGuild(RawGuild):
    welcome_screen: RawWelcomeScreen


class RawGuildCreate(RawGuild):
    joined_at: str
    large: bool
    unavailable: bool
    member_count: int
    voice_states: typing.List[RawVoiceState]
    members: typing.List[RawMember]
    channels: typing.List[RawChannel]
    threads: typing.List[RawThread]
    presences: typing.List[RawPresence]
    stage_instances: typing.List[RawStageInstance]
    guild_scheduled_events: typing.List[RawScheduledEvent]
