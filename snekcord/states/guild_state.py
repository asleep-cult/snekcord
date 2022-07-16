from __future__ import annotations

import typing
from datetime import datetime

from ..enums import CacheFlags, convert_enum
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
from ..json import JSONObject, json_get
from ..objects import (
    CachedGuild,
    Guild,
    GuildExplicitContentFilter,
    GuildFeature,
    GuildIDWrapper,
    GuildMessageNotificationsLevel,
    GuildMFALevel,
    GuildNSFWLevel,
    GuildPremiumTier,
    GuildSystemChannelFlags,
    GuildVerificationLevel,
    PartialGuild,
    RESTGuild,
    SupportsGuildID,
)
from ..snowflake import Snowflake
from ..undefined import undefined
from .base_state import CachedEventState, OnDecoratorT

if typing.TYPE_CHECKING:
    from ..websockets import Shard

__all__ = ('GuildState',)


class GuildState(CachedEventState[SupportsGuildID, Snowflake, CachedGuild, Guild]):
    @property
    def events(self) -> typing.Tuple[str, ...]:
        return tuple(GuildEvents)

    def to_unique(self, object: SupportsGuildID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, PartialGuild):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or PartialGuild')

    def wrap(self, guild: typing.Optional[SupportsGuildID]) -> GuildIDWrapper:
        if guild is not None:
            guild = self.to_unique(guild)

        return GuildIDWrapper(state=self, id=guild)

    async def upsert_cached(
        self, data: JSONObject, flags: CacheFlags = CacheFlags.ALL
    ) -> CachedGuild:
        guild_id = Snowflake.into(data, 'id')
        assert guild_id is not None

        if flags & CacheFlags.ROLES:
            roles = json_get(data, 'roles', typing.List[JSONObject])
            for role in roles:
                role['guild_id'] = guild_id
                await self.client.roles.upsert_cached(role, flags)

        if flags & CacheFlags.EMOJIS:
            emojis = json_get(data, 'emojis', typing.List[JSONObject])
            for emoji in emojis:
                emoji['guild_id'] = guild_id
                await self.client.emojis.upsert_cached(emoji, flags)

        if flags & CacheFlags.CHANNELS:
            channels = json_get(data, 'channels', typing.List[JSONObject], default=())
            for channel in channels:
                channel['guild_id'] = guild_id
                await self.client.channels.upsert_cached(channel, flags)

        if flags & CacheFlags.MEMBERS:
            members = json_get(data, 'members', typing.List[JSONObject], default=())
            for member in members:
                member['guild_id'] = guild_id
                await self.client.members.upsert(member, flags)

        async with self.synchronize(guild_id):
            cached = await self.cache.get(guild_id)

            if cached is None:
                cached = CachedGuild.from_json(data)

                if flags & CacheFlags.GUILDS:
                    await self.cache.create(guild_id, cached)
            else:
                cached.update(data)
                await self.cache.update(guild_id, cached)

        return cached

    async def upsert_rest(self, data: JSONObject) -> RESTGuild:
        guild = await self.upsert(data)

        return RESTGuild.from_guild(
            guild,
            presence_count=json_get(data, 'approximate_presence_count', int, default=None),
            member_count=json_get(data, 'approximate_member_count', int, default=None),
        )

    async def from_cached(self, cached: CachedGuild) -> Guild:
        widget_channel_id = undefined.nullify(cached.widget_channel_id)
        features = [convert_enum(GuildFeature, feature) for feature in cached.features]

        joined_at = undefined.nullify(cached.joined_at)
        if joined_at is not None:
            joined_at = datetime.fromisoformat(joined_at)

        roles = await self.client.roles.for_guild(cached.id)
        emojis = await self.client.emojis.for_guild(cached.id)
        members = await self.client.members.for_guild(cached.id)
        channels = await self.client.channels.for_guild(cached.id)

        return Guild(
            client=self.client,
            id=cached.id,
            name=cached.name,
            icon=cached.icon,
            splash=cached.splash,
            discovery_splash=cached.discovery_splash,
            owner=self.client.users.wrap(cached.owner_id),
            afk_channel=self.client.channels.wrap(cached.afk_channel_id),
            afk_timeout=cached.afk_timeout,
            widget_enabled=undefined.nullify(cached.widget_enabled),
            widget_channel=self.client.channels.wrap(widget_channel_id),
            verification_level=convert_enum(GuildVerificationLevel, cached.verification_level),
            message_notifications_level=convert_enum(
                GuildMessageNotificationsLevel, cached.default_message_notifications
            ),
            explicit_content_filter=convert_enum(
                GuildExplicitContentFilter, cached.explicit_content_filter
            ),
            features=features,
            mfa_level=convert_enum(GuildMFALevel, cached.mfa_level),
            system_channel=self.client.channels.wrap(cached.system_channel_id),
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
            public_updates_channel=self.client.channels.wrap(cached.public_updates_channel_id),
            max_video_channel_users=undefined.nullify(cached.max_video_channel_users),
            nsfw_level=convert_enum(GuildNSFWLevel, cached.nsfw_level),
            roles=roles,
            emojis=emojis,
            members=members,
            channels=channels,
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

        elif event is GuildEvents.AVAILABLE:
            guild = await self.upsert(payload)
            return GuildAvailableEvent(shard=shard, payload=payload, guild=guild)

        elif event is GuildEvents.RECEIVE:
            guild = await self.upsert(payload)
            return GuildReceiveEvent(shard=shard, payload=payload, guild=guild)

        elif event is GuildEvents.UPDATE:
            guild = await self.upsert(payload)
            return GuildUpdateEvent(shard=shard, payload=payload, guild=guild)

        elif event is GuildEvents.DELETE:
            guild = await self.drop(json_get(payload, 'id', str))
            return GuildDeleteEvent(shard=shard, payload=payload, guild=guild)

        assert False
