from __future__ import annotations

import enum
import typing
from datetime import datetime

import attr

from .base import SnowflakeObject
from ..cache import CachedModel
from ..undefined import MaybeUndefined

if typing.TYPE_CHECKING:
    from ..json import JSONObject
    from ..states import (
        ChannelIDWrapper,
        GuildChannelsView,
        GuildEmojisView,
        GuildMembersView,
        GuildRolesView,
        GuildState,
        SupportsGuildID,
        UserIDWrapper,
    )
else:
    SupportsGuildID = typing.NewType('SupportsChannelID', typing.NewType)

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
    id: str
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
    role_ids: typing.List[str]
    emoji_ids: typing.List[str]
    features: typing.List[str]
    mfa_level: int
    application_id: typing.Optional[str]
    system_channel_id: typing.Optional[str]
    system_channel_flags: int
    rules_channel_id: typing.Optional[int]
    joined_at: MaybeUndefined[str]
    voice_state_ids: typing.List[str]
    member_ids: typing.List[str]
    channel_ids: typing.List[str]
    thread_ids: typing.List[str]
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

    async def add_roles(self, state: GuildState, roles: typing.List[JSONObject]) -> None:
        role_ids = [role['id'] for role in roles]
        for role_id in set(self.role_ids) - set(role_ids):
            await state.client.roles.delete(role_id)

        self.role_ids = role_ids
        for role in roles:
            await state.client.roles.upsert(role)

    async def add_emojis(self, state: GuildState, emojis: typing.List[JSONObject]) -> None:
        emoji_ids = [emoji['id'] for emoji in emojis]
        for emoji_id in set(self.emoji_ids) - set(emoji_ids):
            await state.client.emojis.delete(emoji_id)

        self.emoji_ids = emoji_ids
        for emoji in emojis:
            await state.client.emojis.upsert(emoji)

    async def add_channels(self, state: GuildState, channels: typing.List[JSONObject]) -> None:
        channel_ids = [channel['id'] for channel in channels]
        for channel_id in set(self.channel_ids) - set(channel_ids):
            await state.client.channels.delete(channel_id)

        self.channel_ids = channel_ids
        for channel in channels:
            channel['guild_id'] = self.id
            await state.client.channels.upsert(channel)

    async def add_memebers(self, state: GuildState, members: typing.List[JSONObject]) -> None:
        self.member_ids.extend(member['id'] for member in members)

        for member in members:
            await state.client.members.upsert(member)


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
class PartialGuild(SnowflakeObject[SupportsGuildID]):
    state: GuildState

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
    mfa_level: GuildMFALevel = attr.ib()
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
