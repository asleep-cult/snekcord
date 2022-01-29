from __future__ import annotations

import typing
from datetime import datetime

from .base_state import (
    CachedEventState,
    OnDecoratorT,
)
from ..enum import convert_enum
from ..events import (
    BaseEvent,
    GuildAvailableEvent,
    GuildDeleteEvent,
    GuildEvents,
    GuildJoinEvent,
    GuildReceiveEvent,
    GuildUnavailableEvent,
    GuildUpdateEvent,
)
from ..objects import (
    CachedGuild,
    Guild,
    GuildExplicitContentFilter,
    GuildFeature,
    GuildMFALevel,
    GuildMessageNotificationsLevel,
    GuildNSFWLevel,
    GuildPremiumTier,
    GuildSystemChannelFlags,
    GuildVerificationLevel,
    PartialGuild,
    RESTGuild,
    SnowflakeWrapper,
)
from ..snowflake import Snowflake
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from ..json import JSONObject
    from ..websockets import Shard

SupportsGuildID = typing.Union[Snowflake, str, int, PartialGuild]
GuildIDWrapper = SnowflakeWrapper[SupportsGuildID, Guild]


class GuildState(CachedEventState[SupportsGuildID, Snowflake, CachedGuild, Guild]):
    def to_unique(self, object: SupportsGuildID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, PartialGuild):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or PartialGuild')

    async def upsert(self, data: JSONObject) -> Guild:
        guild_id = Snowflake(data['id'])

        async with self.synchronize(guild_id):
            guild = await self.cache.get(guild_id)

            if guild is None:
                guild = CachedGuild.from_json(data)
                await self.cache.create(guild_id, guild)
            else:
                guild.update(data)
                await self.cache.update(guild_id, guild)

        return self.from_cached(guild)

    async def upsert_rest(self, data: JSONObject) -> RESTGuild:
        guild = await self.upsert(data)

        return RESTGuild.from_guild(
            guild,
            presence_count=data.get('approximate_presence_count'),
            member_count=data.get('approximate_member_count'),
        )

    def from_cached(self, cached: CachedGuild) -> Guild:
        guild_id = Snowflake(cached.id)

        widget_channel_id = undefined.nullify(cached.widget_channel_id)
        features = [convert_enum(GuildFeature, feature) for feature in cached.features]

        joined_at = undefined.nullify(cached.joined_at)
        if joined_at is not None:
            joined_at = datetime.fromisoformat(joined_at)

        return Guild(
            state=self,
            id=guild_id,
            name=cached.name,
            icon=cached.icon,
            splash=cached.splash,
            discovery_splash=cached.discovery_splash,
            owner=SnowflakeWrapper(cached.owner_id, state=self.client.users),
            afk_channel=SnowflakeWrapper(cached.afk_channel_id, state=self.client.users),
            afk_timeout=cached.afk_timeout,
            widget_enabled=cached.widget_enabled,
            widget_channel=SnowflakeWrapper(widget_channel_id, state=self.client.channels),
            verification_level=convert_enum(GuildVerificationLevel, cached.verification_level),
            message_notifications_level=convert_enum(
                GuildMessageNotificationsLevel, cached.default_message_notifications
            ),
            explicit_content_filter=convert_enum(
                GuildExplicitContentFilter, cached.explicit_content_filter
            ),
            features=features,
            mfa_level=convert_enum(GuildMFALevel, cached.mfa_level),
            system_channel=SnowflakeWrapper(cached.system_channel_id, state=self.client.channels),
            system_channel_flags=GuildSystemChannelFlags(cached.system_channel_flags),
            joined_at=joined_at,
            max_presences=undefined.nullify(cached.max_presences),
            max_members=undefined.nullify(cached.max_members),
            vanity_url_code=cached.vanity_url_code,
            description=cached.description,
            banner=cached.banner,
            premium_tier=convert_enum(GuildPremiumTier, cached.premium_tier),
            premium_subscription_count=undefined.nullify(cached.premium_subscription_count),
            preferred_locale=cached.preferred_locale,
            public_updates_channel=SnowflakeWrapper(
                cached.public_updates_channel_id, state=self.client.channels
            ),
            max_video_channel_users=undefined.nullify(cached.max_video_channel_users),
            nsfw_level=convert_enum(GuildNSFWLevel, cached.nsfw_level),
            roles=self.client.create_guild_roles_view(cached.role_ids, guild_id),
            emojis=self.client.create_guild_emojis_view(cached.emoji_ids, guild_id),
            members=self.client.create_guild_members_view(cached.member_ids, guild_id),
            channels=self.client.create_guild_channels_view(cached.channel_ids, guild_id),
        )

    def on_join(self) -> OnDecoratorT[GuildJoinEvent]:
        return self.on(GuildEvents.JOIN)

    def on_available(self) -> OnDecoratorT[GuildAvailableEvent]:
        return self.on(GuildEvents.AVAILABLE)

    def on_receive(self) -> OnDecoratorT[GuildReceiveEvent]:
        return self.on(GuildEvents.RECEIVE)

    def on_update(self) -> OnDecoratorT[GuildUpdateEvent]:
        return self.on(GuildEvents.UPDATE)

    def on_delete(self) -> OnDecoratorT[GuildDeleteEvent]:
        return self.on(GuildEvents.DELETE)

    def on_unavailable(self) -> OnDecoratorT[GuildUnavailableEvent]:
        return self.on(GuildEvents.UNAVAILABLE)

    async def create_event(self, event: str, shard: Shard, payload: JSONObject) -> BaseEvent:
        event = GuildEvents(event)

        if event is GuildEvents.JOIN:
            guild = await self.upsert(payload)
            return GuildJoinEvent(shard=shard, payload=payload, guild=guild)

        if event is GuildEvents.AVAILABLE:
            guild = await self.upsert(payload)
            return GuildAvailableEvent(shard=shard, payload=payload, guild=guild)

        if event is GuildEvents.RECEIVE:
            guild = await self.upsert(payload)
            return GuildReceiveEvent(shard=shard, payload=payload, guild=guild)

        if event is GuildEvents.DELETE:
            guild = await self.delete(payload['id'])
            return GuildDeleteEvent(shard=shard, payload=payload, guild=guild)
