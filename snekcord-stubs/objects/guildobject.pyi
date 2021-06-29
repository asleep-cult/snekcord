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
from ..enums import (
    ExplicitContentFilterLevel,
    GuildFeature,
    GuildNSFWLevel,
    MFALevel,
    MessageNotificationsLevel,
    PremiumTier,
    VerificationLevel)
from ..flags import SystemChannelFlags
from ..states.channelstate import GuildChannelState
from ..states.emojistate import GuildEmojiState
from ..states.guildstate import GuildBanState, GuildState
from ..states.integrationstate import GuildIntegrationState
from ..states.memberstate import GuildMemberState
from ..states.rolestate import RoleState
from ..typedefs import Json
from ..utils.json import JsonArray, JsonField, JsonObject
from ..utils.snowflake import Snowflake


class Guild(BaseObject[Snowflake]):
    name: t.ClassVar[JsonField[str]]
    icon: t.ClassVar[JsonField[str]]
    icon_hash: t.ClassVar[JsonField[str]]
    splash: t.ClassVar[JsonField[str]]
    discovery_splash: t.ClassVar[JsonField[str]]
    features: t.ClassVar[JsonArray[GuildFeature]]
    member_count: t.ClassVar[JsonField[int]]
    presence_count: t.ClassVar[JsonField[int]]
    description: t.ClassVar[JsonField[str]]
    owner: t.ClassVar[JsonField[bool]]
    owner_id: t.ClassVar[JsonField[Snowflake]]
    permissions: t.ClassVar[JsonField[str]]
    region: t.ClassVar[JsonField[str]]
    afk_channel_id: t.ClassVar[JsonField[Snowflake]]
    afk_timeout: t.ClassVar[JsonField[int]]
    verification_level: t.ClassVar[JsonField[VerificationLevel]]
    default_message_notifications: t.ClassVar[JsonField[MessageNotificationsLevel]]
    explicit_content_filter: t.ClassVar[JsonField[ExplicitContentFilterLevel]]
    mfa_level: t.ClassVar[JsonField[MFALevel]]
    application_id: t.ClassVar[JsonField[Snowflake]]
    system_channel_id: t.ClassVar[JsonField[Snowflake]]
    system_channel_flags: t.ClassVar[JsonField[SystemChannelFlags]]
    rules_channel_id: t.ClassVar[JsonField[Snowflake]]
    joined_at: t.ClassVar[JsonField[datetime]]
    large: t.ClassVar[JsonField[bool]]
    unavailable: t.ClassVar[JsonField[bool]]
    max_presences: t.ClassVar[JsonField[int]]
    max_members: t.ClassVar[JsonField[int]]
    banner: t.ClassVar[JsonField[str]]
    premium_tier: t.ClassVar[JsonField[PremiumTier]]
    premium_subscription_count: t.ClassVar[JsonField[int]]
    preferred_locale: t.ClassVar[JsonField[str]]
    public_updates_channel_id: t.ClassVar[JsonField[Snowflake]]
    max_video_channel_users: t.ClassVar[JsonField[int]]
    nsfw_level: t.ClassVar[JsonField[GuildNSFWLevel]]

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
    reason: t.ClassVar[JsonField[str]]

    state: GuildBanState
    user: User
    guild: Guild

    async def revoke(self) -> None: ...


class WelcomeScreenChannel(JsonObject):
    channel_id: t.ClassVar[JsonField[Snowflake]]
    description: t.ClassVar[JsonField[str]]
    emoji_id: t.ClassVar[JsonField[str]]
    emoji_name: t.ClassVar[JsonField[str]]

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
