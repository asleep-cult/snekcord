from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .emojiobject import BuiltinEmoji, GuildEmoji
from .inviteobject import GuildVanityURL, Invite
from .templateobject import GuildTemplate
from .userobject import User
from .widgetobject import GuildWidget
from ..states.channelstate import GuildChannelState
from ..states.emojistate import GuildEmojiState
from ..states.guildstate import GuildBanState, GuildState
from ..states.integrationstate import GuildIntegrationState
from ..states.memberstate import GuildMemberState
from ..states.rolestate import RoleState
from ..typedefs import Json
from ..utils.bitset import Bitset, Flag
from ..utils.enum import Enum
from ..utils.json import JsonArray, JsonField, JsonObject
from ..utils.snowflake import Snowflake


class MessageNotificationsLevel(Enum[int]):
    ALL_MESSAGES: t.ClassVar[int]
    ONLY_MENTIONS: t.ClassVar[int]


class ExplicitContentFilterLevel(Enum[int]):
    DISABLED: t.ClassVar[int]
    MEMBERS_WITHOUT_ROLES: t.ClassVar[int]
    ALL_MEMBERS: t.ClassVar[int]


class MFALevel(Enum[int]):
    NONE: t.ClassVar[int]
    ELEVATED: t.ClassVar[int]


class VerificationLevel(Enum[int]):
    NONE: t.ClassVar[int]
    LOW: t.ClassVar[int]
    MEDIUM: t.ClassVar[int]
    HIGH: t.ClassVar[int]
    VERY_HIGH: t.ClassVar[int]


class GuildNSFWLevel(Enum[int]):
    DEFAULT: t.ClassVar[int]
    EXPLICIT: t.ClassVar[int]
    SAFE: t.ClassVar[int]
    AGE_RESTRICTED: t.ClassVar[int]


class PremiumTier(Enum[int]):
    NONE: t.ClassVar[int]
    TIER_1: t.ClassVar[int]
    TIER_2: t.ClassVar[int]
    TIER_3: t.ClassVar[int]


class SystemChannelFlags(Bitset):
    SUPPRESS_JOIN_NOTIFICATIONS: t.ClassVar[Flag]
    SUPPRESS_PREMIUM_SUBSCRIPTIONS: t.ClassVar[Flag]
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS: t.ClassVar[Flag]


class GuildFeature(Enum[str]):
    ANIMATED_ICON: t.ClassVar[str]
    BANNER: t.ClassVar[str]
    COMMERCE: t.ClassVar[str]
    COMMUNITY: t.ClassVar[str]
    DISCOVERABLE: t.ClassVar[str]
    FEATURABLE: t.ClassVar[str]
    INVITE_SPLASH: t.ClassVar[str]
    MEMBER_VERIFIVATION_GATE_ENABLED: t.ClassVar[str]
    NEWS: t.ClassVar[str]
    PARTNERED: t.ClassVar[str]
    PREVIEW_ENABLED: t.ClassVar[str]
    VANITY_URL: t.ClassVar[str]
    VERIFIED: t.ClassVar[str]
    VIP_REGIONS: t.ClassVar[str]
    WELCOME_SCREEN_ENABLED: t.ClassVar[str]
    TICKETED_EVENTS_ENABLED: t.ClassVar[str]
    MONETIZATION_ENABLED: t.ClassVar[str]
    MORE_STICKERS: t.ClassVar[str]


class Guild(BaseObject[Snowflake]):
    name: JsonField[str]
    icon: JsonField[str]
    icon_hash: JsonField[str]
    splash: JsonField[str]
    discovery_splash: JsonField[str]
    features: JsonArray[GuildFeature]
    member_count: JsonField[int]
    presence_count: JsonField[int]
    description: JsonField[str]
    owner: JsonField[bool]
    owner_id: JsonField[Snowflake]
    permissions: JsonField[str]
    region: JsonField[str]
    afk_channel_id: JsonField[Snowflake]
    afk_timeout: JsonField[int]
    verification_level: JsonField[VerificationLevel]
    default_message_notifications: JsonField[MessageNotificationsLevel]
    explicit_content_filter: JsonField[ExplicitContentFilterLevel]
    mfa_level: JsonField[MFALevel]
    application_id: JsonField[Snowflake]
    system_channel_id: JsonField[Snowflake]
    system_channel_flags: JsonField[SystemChannelFlags]
    rules_channel_id: JsonField[Snowflake]
    joined_at: JsonField[datetime]
    large: JsonField[bool]
    unavailable: JsonField[bool]
    max_presences: JsonField[int]
    max_members: JsonField[int]
    banner: JsonField[str]
    premium_tier: JsonField[PremiumTier]
    premium_subscription_count: JsonField[int]
    preferred_locale: JsonField[str]
    public_updates_channel_id: JsonField[Snowflake]
    max_video_channel_users: JsonField[int]
    nsfw_level: JsonField[GuildNSFWLevel]

    state: GuildState
    unsynced: bool
    bans: GuildBanState
    channels: GuildChannelState
    emojis: GuildEmojiState
    roles: RoleState
    members: GuildMemberState
    integrations: GuildIntegrationState
    widget: GuildWidget
    vanity_url: GuildVanityURL
    welcome_screen: WelcomeScreen

    def __init__(self, *, state: GuildState) -> None: ...

    async def sync(self, payload: Json) -> None: ...

    async def modify(self, **kwargs: t.Any) -> Guild: ...

    async def delete(self) -> None: ...

    async def prune(self, **kwargs: t.Any) -> int | None: ...

    async def fetch_preview(self) -> Guild: ...

    async def fetch_voice_reagions(self) -> list[str]: ...

    async def fetch_invites(self) -> set[Invite]: ...

    async def fetch_templates(self) -> set[GuildTemplate]: ...

    async def create_template(self, **kwargs: t.Any) -> GuildTemplate: ...

    def to_preview_dict(self) -> Json: ...


class GuildBan(BaseObject[Snowflake]):
    reason: JsonField[str]

    state: GuildBanState
    user: User
    guild: Guild

    async def revoke(self) -> None: ...


class WelcomeScreenChannel(JsonObject):
    channel_id: JsonField[Snowflake]
    description: JsonField[str]
    emoji_id: JsonField[str]
    emoji_name: JsonField[str]

    welcome_screen: WelcomeScreen

    def __init__(self, *, welcome_screen: WelcomeScreen) -> None: ...

    @property
    def channel(self) -> GuildChannel | None: ...

    @property
    def emoji(self) -> BuiltinEmoji | GuildEmoji: ...


class WelcomeScreen(JsonObject):
    guild: Guild
    welcome_channels: list[WelcomeScreenChannel]

    def __init__(self, *, guild: Guild) -> None: ...

    async def fetch(self) -> WelcomeScreen: ...

    async def modify(self, **kwargs: t.Any) -> WelcomeScreen: ...
