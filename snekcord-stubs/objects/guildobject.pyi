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
from ..utils.json import JsonObject, JsonTemplate
from ..utils.snowflake import Snowflake


class MessageNotificationsLevel(Enum[int]):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class ExplicitContentFilterLevel(Enum[int]):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class MFALevel(Enum[int]):
    NONE = 0
    ELEVATED = 1


class VerificationLevel(Enum[int]):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class GuildNSFWLevel(Enum[int]):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class PremiumTier(Enum[int]):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class SystemChannelFlags(Bitset):
    SUPPRESS_JOIN_NOTIFICATIONS = Flag(0)
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = Flag(1)
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = Flag(2)


class GuildFeature(Enum[str]):
    ANIMATED_ICON = 'ANIMATED_ICON'
    BANNER = 'BANNER'
    COMMERCE = 'COMMERCE'
    COMMUNITY = 'COMMUNITY'
    DISCOVERABLE = 'DISCOVERABLE'
    FEATURABLE = 'FEATURABLE'
    INVITE_SPLASH = 'INVITE_SPLASH'
    MEMBER_VERIFIVATION_GATE_ENABLED = 'MEMBER_VEFIFICATION_GATE_ENNABLED'
    NEWS = 'NEWS'
    PARTNERED = 'PARTNERED'
    PREVIEW_ENABLED = 'PREVIEW_ENABLED'
    VANITY_URL = 'VANITY_URL'
    VERIFIED = 'VERIFIED'
    VIP_REGIONS = 'VIP_REGIONS'
    WELCOME_SCREEN_ENABLED = 'WELCOME_SCREEN_ENABLED'
    TICKETED_EVENTS_ENABLED = 'TICKETED_EVENTS_ENABLED'
    MONETIZATION_ENABLED = 'MONETIZATION_ENABLED'
    MORE_STICKERS = 'MORE_STICKERS'


GuildPreviewTemplate: JsonTemplate = ...
GuildTemplate: JsonTemplate = ...


class Guild(BaseObject[Snowflake], template=GuildTemplate):
    name: str
    icon: str
    icon_hash: str
    splash: str
    discovery_splash: str
    features: list[GuildFeature]
    member_count: int
    presence_count: int
    description: str
    owner: bool
    owner_id: Snowflake
    permissions: str
    region: str
    afk_channel_id: Snowflake
    afk_timeout: int
    verification_level: VerificationLevel
    default_message_notifications: MessageNotificationsLevel
    explicit_content_filter: ExplicitContentFilterLevel
    mfa_level: MFALevel
    application_id: Snowflake
    system_channel_id: Snowflake
    system_channel_flags: SystemChannelFlags
    rules_channel_id: Snowflake
    joined_at: datetime
    large: bool
    unavailable: bool
    max_presences: int
    max_members: int
    banner: str
    premium_tier: PremiumTier
    premium_subscription_count: int
    preferred_locale: str
    public_updates_channel_id: Snowflake
    max_video_channel_users: int
    nsfw_level: GuildNSFWLevel

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


GuildBanTemplate: JsonTemplate = ...


class GuildBan(BaseObject[Snowflake], template=GuildBanTemplate):
    reason: str
    user: User

    state: GuildBanState
    guild: Guild

    async def revoke(self) -> None: ...


WelcomeScreenChannelTemplate: JsonTemplate = ...


class WelcomeScreenChannel(JsonObject, template=WelcomeScreenChannelTemplate):
    channel_id: Snowflake
    description: str
    emoji_id: str
    emoji_name: str
    welcome_screen: WelcomeScreen

    def __init__(self, *, welcome_screen: WelcomeScreen) -> None: ...

    @property
    def channel(self) -> GuildChannel | None: ...

    @property
    def emoji(self) -> BuiltinEmoji | GuildEmoji: ...


WelcomeScreenTemplate: JsonTemplate = ...


class WelcomeScreen(JsonObject, template=WelcomeScreenTemplate):
    guild: Guild
    welcome_channels: list[WelcomeScreenChannel]

    def __init__(self, *, guild: Guild) -> None: ...

    async def fetch(self) -> WelcomeScreen: ...

    async def modify(self, **kwargs: t.Any) -> WelcomeScreen: ...
