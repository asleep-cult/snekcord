from __future__ import annotations

import typing
from datetime import datetime

from ..builders import ChannelCreateBuilder, ChannelPositionsBuilder
from ..cache import RefStore, SnowflakeMemoryRefStore
from ..enum import convert_enum
from ..events import (
    BaseEvent,
    ChannelCreateEvent,
    ChannelDeleteEvent,
    ChannelEvents,
    ChannelPinsUpdateEvent,
    ChannelUpdateEvent,
)
from ..json import JSONObject, JSONType, json_get
from ..objects import (
    BaseChannel,
    CachedChannel,
    CategoryChannel,
    ChannelType,
    SnowflakeWrapper,
    TextChannel,
    VoiceChannel,
)
from ..rest.endpoints import (
    DELETE_CHANNEL,
    GET_CHANNEL,
    GET_GUILD_CHANNELS,
    TRIGGER_CHANNEL_TYPING,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined
from .base_state import CachedEventState, CachedStateView, CacheFlags, OnDecoratorT

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..websockets import Shard
    from .guild_state import SupportsGuildID

__all__ = (
    'SupportsChannelID',
    'ChannelIDWrapper',
    'ChannelState',
    'GuildChannelsView',
)

SupportsChannelID = typing.Union[Snowflake, str, int, BaseChannel]
ChannelIDWrapper = SnowflakeWrapper[SupportsChannelID, BaseChannel]


class ChannelState(CachedEventState[SupportsChannelID, Snowflake, CachedChannel, BaseChannel]):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.guild_refstore = self.create_guild_refstore()

    def create_guild_refstore(self) -> RefStore[Snowflake, Snowflake]:
        return SnowflakeMemoryRefStore()

    @property
    def events(self) -> typing.Tuple[str, ...]:
        return tuple(ChannelEvents)

    def to_unique(self, object: SupportsChannelID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, BaseChannel):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or BaseChannel')

    async def for_guild(self, guild: SupportsGuildID) -> GuildChannelsView:
        guild_id = self.client.guilds.to_unique(guild)

        channels = await self.guild_refstore.get(guild_id)
        return self.client.create_guild_channels_view(channels, guild_id)

    def inject_metadata(self, data: JSONType, guild_id: Snowflake) -> JSONObject:
        if not isinstance(data, dict):
            raise TypeError('data should be a JSON object')

        return dict(data, guild_id=guild_id)

    async def upsert_cached(
        self, data: JSONObject, flags: CacheFlags = CacheFlags.ALL
    ) -> CachedChannel:
        channel_id = Snowflake.into(data, 'id')
        assert channel_id is not None

        guild_id = Snowflake.into(data, 'guild_id')
        if guild_id is not None:
            await self.guild_refstore.add(guild_id, channel_id)

        async with self.synchronize(channel_id):
            cached = await self.cache.get(channel_id)

            if cached is None:
                cached = CachedChannel.from_json(data)
                await self.cache.create(channel_id, cached)
            else:
                cached.update(data)
                await self.cache.update(channel_id, cached)

        return cached

    async def from_cached(self, cached: CachedChannel) -> BaseChannel:
        cached.id = Snowflake(cached.id)
        type = convert_enum(ChannelType, cached.type)

        if type is ChannelType.GUILD_CATEGORY:
            assert (
                cached.guild_id is not undefined
                and cached.name is not undefined
                and cached.position is not undefined
            ), 'Invalid GUILD_CATEGORY channel'

            return CategoryChannel(
                client=self.client,
                id=cached.id,
                type=type,
                guild=SnowflakeWrapper(cached.guild_id, state=self.client.guilds),
                name=cached.name,
                position=cached.position,
            )

        if type is ChannelType.GUILD_TEXT:
            assert (
                cached.guild_id is not undefined
                and cached.name is not undefined
                and cached.position is not undefined
                and cached.rate_limit_per_user is not undefined
                and cached.last_message_id is not undefined
            ), 'Invalid GUILD_TEXT channel'

            parent_id = undefined.nullify(cached.parent_id)

            last_pin_timestamp = undefined.nullify(cached.last_pin_timestamp)
            if last_pin_timestamp is not None:
                last_pin_timestamp = datetime.fromisoformat(last_pin_timestamp)

            messages = await self.client.messages.for_channel(cached.id)

            return TextChannel(
                client=self.client,
                id=cached.id,
                type=type,
                guild=SnowflakeWrapper(cached.guild_id, state=self.client.guilds),
                parent=SnowflakeWrapper(parent_id, state=self.client.channels),
                name=cached.name,
                position=cached.position,
                nsfw=cached.nsfw if cached.nsfw is not undefined else False,
                rate_limit_per_user=cached.rate_limit_per_user,
                last_message=SnowflakeWrapper(cached.last_message_id, state=self.client.messages),
                last_pin_timestamp=last_pin_timestamp,
                messages=messages,
            )

        if type is ChannelType.GUILD_VOICE:
            assert (
                cached.guild_id is not undefined
                and cached.name is not undefined
                and cached.position is not undefined
                and cached.bitrate is not undefined
                and cached.user_limit is not undefined
                and cached.rtc_region is not undefined
            ), 'Invalid GUILD_VOICE channel'

            parent_id = undefined.nullify(cached.parent_id)

            return VoiceChannel(
                client=self.client,
                id=cached.id,
                type=type,
                guild=SnowflakeWrapper(cached.guild_id, state=self.client.guilds),
                parent=SnowflakeWrapper(parent_id, state=self.client.channels),
                name=cached.name,
                position=cached.position,
                nsfw=cached.nsfw if cached.nsfw is not undefined else False,
                bitrate=cached.bitrate,
                user_limit=cached.user_limit,
                rtc_region=cached.rtc_region,
            )

        return BaseChannel(client=self.client, id=cached.id, type=type)

    async def remove_refs(self, object: CachedChannel) -> None:
        if object.guild_id is not undefined:
            await self.guild_refstore.remove(object.guild_id, object.id)

    async def trigger_typing(self, channel: SupportsChannelID) -> None:
        await self.client.rest.request_api(
            TRIGGER_CHANNEL_TYPING, channel_id=self.client.channels.to_unique(channel)
        )

    async def fetch(self, channel: SupportsChannelID) -> BaseChannel:
        channel_id = self.to_unique(channel)

        data = await self.client.rest.request_api(GET_CHANNEL, channel_id=channel_id)
        assert isinstance(data, dict)

        return await self.upsert(self.inject_metadata(data, channel_id))

    async def fetch_all(self, guild: SupportsGuildID) -> typing.List[BaseChannel]:
        guild_id = self.client.guilds.to_unique(guild)

        data = await self.client.rest.request_api(GET_GUILD_CHANNELS, guild_id=guild_id)
        assert isinstance(data, list)

        iterator = (self.inject_metadata(channel, guild_id) for channel in data)
        return [await self.upsert(channel) for channel in iterator]

    def create(
        self,
        guild: SupportsGuildID,
        *,
        name: MaybeUndefined[str] = undefined,
        type: MaybeUndefined[ChannelType] = undefined,
        topic: MaybeUndefined[str] = undefined,
        bitrate: MaybeUndefined[int] = undefined,
        user_limit: MaybeUndefined[int] = undefined,
        rate_limit_per_user: MaybeUndefined[int] = undefined,
        position: MaybeUndefined[int] = undefined,
        parent: MaybeUndefined[SupportsChannelID] = undefined,
        nsfw: MaybeUndefined[bool] = undefined,
    ) -> ChannelCreateBuilder:
        builder = ChannelCreateBuilder(
            client=self.client, guild_id=self.client.guilds.to_unique(guild)
        )

        return builder.setters(
            name=name,
            type=type,
            topic=topic,
            bitrate=bitrate,
            user_limit=user_limit,
            rate_limit_per_user=rate_limit_per_user,
            position=position,
            parent=parent,
            nsfw=nsfw,
        )

    def update_positions(self, guild: SupportsGuildID) -> ChannelPositionsBuilder:
        return ChannelPositionsBuilder(
            client=self.client, guild_id=self.client.guilds.to_unique(guild)
        )

    async def delete(self, channel: SupportsChannelID) -> typing.Optional[BaseChannel]:
        channel_id = self.client.channels.to_unique(channel)

        await self.client.rest.request_api(DELETE_CHANNEL, channel_id=channel_id)
        return await self.drop(channel_id)

    def on_create(self) -> OnDecoratorT[ChannelCreateEvent]:
        return self.on(ChannelEvents.CREATE)

    def on_update(self) -> OnDecoratorT[ChannelUpdateEvent]:
        return self.on(ChannelEvents.UPDATE)

    def on_delete(self) -> OnDecoratorT[ChannelDeleteEvent]:
        return self.on(ChannelEvents.DELETE)

    def on_pins_update(self) -> OnDecoratorT[ChannelPinsUpdateEvent]:
        return self.on(ChannelEvents.PINS_UPDATE)

    async def create_event(self, event: str, shard: Shard, payload: JSONObject) -> BaseEvent:
        event = ChannelEvents(event)

        guild_id = json_get(payload, 'guild_id', str, default=None)
        guild = SnowflakeWrapper(guild_id, state=self.client.guilds)

        if event is ChannelEvents.CREATE:
            channel = await self.upsert(payload)
            return ChannelCreateEvent(shard=shard, payload=payload, guild=guild, channel=channel)

        elif event is ChannelEvents.UPDATE:
            channel = await self.upsert(payload)
            return ChannelUpdateEvent(shard=shard, payload=payload, guild=guild, channel=channel)

        elif event is ChannelEvents.DELETE:
            channel = await self.drop(json_get(payload, 'id', str))
            return ChannelDeleteEvent(shard=shard, payload=payload, guild=guild, channel=channel)

        elif event is ChannelEvents.PINS_UPDATE:
            channel = await self.get(json_get(payload, 'channel_id', str))

            timestamp = json_get(payload, 'timestamp', typing.Optional[str])
            if timestamp is not None:
                timestamp = datetime.fromisoformat(timestamp)

            return ChannelPinsUpdateEvent(
                shard=shard, payload=payload, guild=guild, channel=channel, timestamp=timestamp
            )


class GuildChannelsView(CachedStateView[SupportsChannelID, Snowflake, BaseChannel]):
    def __init__(
        self,
        *,
        state: ChannelState,
        channels: typing.Iterable[SupportsChannelID],
        guild: SupportsGuildID,
    ) -> None:
        super().__init__(state=state, keys=channels)
        self.guild_id = self.client.guilds.to_unique(guild)

    async def fetch_all(self) -> typing.List[BaseChannel]:
        return await self.client.channels.fetch_all(self.guild_id)

    def create(
        self,
        *,
        name: MaybeUndefined[str] = undefined,
        type: MaybeUndefined[ChannelType] = undefined,
        topic: MaybeUndefined[str] = undefined,
        bitrate: MaybeUndefined[int] = undefined,
        user_limit: MaybeUndefined[int] = undefined,
        rate_limit_per_user: MaybeUndefined[int] = undefined,
        position: MaybeUndefined[int] = undefined,
        parent: MaybeUndefined[SupportsChannelID] = undefined,
        nsfw: MaybeUndefined[bool] = undefined,
    ) -> ChannelCreateBuilder:
        return self.client.channels.create(
            self.guild_id,
            name=name,
            type=type,
            topic=topic,
            bitrate=bitrate,
            user_limit=user_limit,
            rate_limit_per_user=rate_limit_per_user,
            position=position,
            parent=parent,
            nsfw=nsfw,
        )

    def update_position(self) -> ChannelPositionsBuilder:
        return self.client.channels.update_positions(self.guild_id)
