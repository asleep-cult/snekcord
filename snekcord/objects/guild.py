from __future__ import annotations

import typing
from datetime import datetime

import attr

from ..api import (
    GuildExplicitContentFilter,
    GuildFeature,
    GuildMessageNotificationsLevel,
    GuildMFALevel,
    GuildNSFWLevel,
    GuildPremiumTier,
    GuildSystemChannelFlags,
    GuildVerificationLevel,
)
from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined
from .base import SnowflakeObject, SnowflakeWrapper

if typing.TYPE_CHECKING:
    from ..states import (
        GuildChannelsView,
        GuildEmojisView,
        GuildMembersView,
        GuildRolesView,
    )
    from .channel import ChannelIDWrapper
    from .user import UserIDWrapper

__all__ = (
    'SupportsGuildID',
    'CachedGuild',
    'PartialGuild',
    'GuildPreview',
    'Guild',
    'RESTGuild',
    'GuildIDWrapper',
)

SupportsGuildID = typing.Union[Snowflake, str, int, 'PartialGuild']


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


GuildIDWrapper = SnowflakeWrapper[SupportsGuildID, Guild]
