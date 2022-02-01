from __future__ import annotations

import typing
from datetime import datetime

from .base_state import (
    CachedEventState,
    CachedStateView,
    OnDecoratorT,
)
from ..cache import (
    RefStore,
    SnowflakeMemoryRefStore,
)
from ..enum import convert_enum
from ..events import (
    BaseEvent,
    ChannelCreateEvent,
    ChannelDeleteEvent,
    ChannelEvents,
    ChannelPinsUpdateEvent,
    ChannelUpdateEvent,
)
from ..objects import (
    BaseChannel,
    CachedChannel,
    CategoryChannel,
    ChannelType,
    SnowflakeWrapper,
    TextChannel,
    VoiceChannel,
)
from ..snowflake import Snowflake
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from .guild_state import SupportsGuildID
    from ..clients import Client
    from ..json import JSONObject
    from ..websockets import Shard

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
        self.message_refstore = self.create_message_refstore()

    @property
    def events(self) -> typing.Tuple[str, ...]:
        return tuple(ChannelEvents)

    def create_message_refstore(self) -> RefStore[Snowflake, Snowflake]:
        return SnowflakeMemoryRefStore()

    def to_unique(self, object: SupportsChannelID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, BaseChannel):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or BaseChannel')

    async def upsert(self, data: JSONObject) -> BaseChannel:
        channel_id = Snowflake.into(data, 'id')
        assert channel_id is not None

        guild_id = Snowflake.into(data, 'guild_id')
        if guild_id is not None:
            await self.client.guilds.channel_refstore.add(guild_id, channel_id)

        async with self.synchronize(channel_id):
            channel = await self.cache.get(channel_id)

            if channel is None:
                channel = CachedChannel.from_json(data)
                await self.cache.create(channel_id, channel)
            else:
                channel.update(data)
                await self.cache.update(channel_id, channel)

        return await self.from_cached(channel)

    async def from_cached(self, cached: CachedChannel) -> BaseChannel:
        channel_id = Snowflake(cached.id)
        type = convert_enum(ChannelType, cached.type)

        message_ids = await self.message_refstore.get(cached.id)

        if type is ChannelType.GUILD_CATEGORY:
            assert (
                cached.guild_id is not undefined
                and cached.name is not undefined
                and cached.position is not undefined
            ), 'Invalid GUILD_CATEGORY channel'

            return CategoryChannel(
                state=self,
                id=channel_id,
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

            return TextChannel(
                state=self,
                id=channel_id,
                type=type,
                guild=SnowflakeWrapper(cached.guild_id, state=self.client.guilds),
                parent=SnowflakeWrapper(parent_id, state=self.client.channels),
                name=cached.name,
                position=cached.position,
                nsfw=cached.nsfw if cached.nsfw is not undefined else False,
                rate_limit_per_user=cached.rate_limit_per_user,
                last_message=SnowflakeWrapper(cached.last_message_id, state=self.client.messages),
                last_pin_timestamp=last_pin_timestamp,
                messages=self.client.create_channel_messages_view(message_ids, channel_id),
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
                state=self,
                id=channel_id,
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

        return BaseChannel(state=self, id=channel_id, type=type)

    async def remove_refs(self, object: CachedChannel) -> None:
        if object.guild_id is not undefined:
            await self.client.guilds.channel_refstore.remove(object.guild_id, object.id)

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

        guild = SnowflakeWrapper(payload['guild_id'], state=self.client.guilds)

        if event is ChannelEvents.CREATE:
            channel = await self.upsert(payload)
            return ChannelCreateEvent(shard=shard, payload=payload, guild=guild, channel=channel)

        elif event is ChannelEvents.UPDATE:
            channel = await self.upsert(payload)
            return ChannelUpdateEvent(shard=shard, payload=payload, guild=guild, channel=channel)

        elif event is ChannelEvents.DELETE:
            channel = await self.delete(payload['id'])
            return ChannelDeleteEvent(shard=shard, payload=payload, guild=guild, channel=channel)

        elif event is ChannelEvents.PINS_UPDATE:
            channel = await self.get(payload['channel_id'])

            timestamp = payload.get('timestamp')
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
