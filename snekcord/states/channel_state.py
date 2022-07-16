from __future__ import annotations

import typing
from datetime import datetime

from ..api import (
    ChannelAPI,
    RawChannelCreate,
    RawChannelDelete,
    RawChannelPinsUpdate,
    RawChannelTypes,
    RawChannelUpdate,
)
from ..builders import ChannelCreateBuilder, ChannelPositionsBuilder
from ..cache import RefStore, SnowflakeMemoryRefStore
from ..enums import CacheFlags, convert_enum
from ..events import (
    ChannelCreateEvent,
    ChannelDeleteEvent,
    ChannelEvents,
    ChannelPinsUpdateEvent,
    ChannelUpdateEvent,
)
from ..objects import (
    CachedChannel,
    CategoryChannel,
    Channel,
    ChannelIDWrapper,
    ChannelType,
    SupportsChannelID,
    SupportsGuildID,
    TextChannel,
    VoiceChannel,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined
from .base_state import CachedEventState, CachedStateView, OnDecoratorT

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..websockets import Shard

__all__ = ('ChannelState', 'GuildChannelsView')


class ChannelState(CachedEventState[SupportsChannelID, Snowflake, CachedChannel, Channel]):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.api = self.create_api()
        self.guild_refstore = self.create_guild_refstore()

    def create_api(self) -> ChannelAPI:
        return ChannelAPI(client=self.client)

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

        elif isinstance(object, Channel):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or BaseChannel')

    def wrap(self, channel: typing.Optional[SupportsChannelID]) -> ChannelIDWrapper:
        if channel is not None:
            channel = self.to_unique(channel)

        return ChannelIDWrapper(state=self, id=channel)

    async def for_guild(self, guild: SupportsGuildID) -> GuildChannelsView:
        """Create a cache view for a specific guild. If you have a guild object
        consider using the `snekcord.Guild.channels` attribute instead.

        Parameters
        ----------
        guild: snekcord.SupportsGuildID
            The guild or id of the guild to create the view for.

        Returns
        -------
        snekcord.GuildChannelsView
            An immutable view containing every cached channel in the guild.

        Example
        -------
        ```py
        channels = await client.channnels.for_guild(834890063581020210)

        async for channel in channels:
            print(f'{channel.name}  (ID: {channel.id})')
        ```
        """
        guild_id = self.client.guilds.to_unique(guild)

        channels = await self.guild_refstore.get(guild_id)
        return self.client.create_guild_channels_view(channels, guild_id)

    async def upsert_cached(
        self, data: RawChannelTypes, flags: CacheFlags = CacheFlags.ALL
    ) -> CachedChannel:
        channel_id = data['id']

        guild_id = data.get('guild_id')
        if guild_id is not None and flags & CacheFlags.GUILDS:
            await self.guild_refstore.add(guild_id, channel_id)

        async with self.synchronize(channel_id):
            cached = await self.cache.get(channel_id)

            if cached is None:
                cached = CachedChannel.from_json(data)

                if flags & CacheFlags.CHANNELS:
                    await self.cache.create(channel_id, cached)
            else:
                cached.update(data)
                await self.cache.update(channel_id, cached)

        return cached

    async def from_cached(self, cached: CachedChannel) -> Channel:
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
                guild=self.client.guilds.wrap(cached.guild_id),
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
                guild=self.client.guilds.wrap(cached.guild_id),
                parent=self.client.channels.wrap(parent_id),
                name=cached.name,
                position=cached.position,
                nsfw=cached.nsfw if cached.nsfw is not undefined else False,
                rate_limit_per_user=cached.rate_limit_per_user,
                last_message=self.client.messages.wrap(cached.last_message_id),
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
                guild=self.client.guilds.wrap(cached.guild_id),
                parent=self.client.channels.wrap(parent_id),
                name=cached.name,
                position=cached.position,
                nsfw=cached.nsfw if cached.nsfw is not undefined else False,
                bitrate=cached.bitrate,
                user_limit=cached.user_limit,
                rtc_region=cached.rtc_region,
            )

        assert cached.name is not undefined
        return Channel(client=self.client, id=cached.id, type=type, name=cached.name)

    async def remove_refs(self, object: CachedChannel) -> None:
        if object.guild_id is not undefined:
            await self.guild_refstore.remove(object.guild_id, object.id)

    async def trigger_typing(self, channel: SupportsChannelID) -> None:
        channel_id = self.to_unique(channel)
        await self.api.trigger_channel_typing(channel_id)

    async def fetch(self, channel: SupportsChannelID) -> Channel:
        channel_id = self.to_unique(channel)

        data = await self.api.get_channel(channel_id)
        return await self.upsert(data)

    async def fetch_all(self, guild: SupportsGuildID) -> typing.List[Channel]:
        guild_id = self.client.guilds.to_unique(guild)

        channels = await self.api.get_guild_channels(guild_id)
        return [await self.upsert(channel) for channel in channels]

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

    async def delete(self, channel: SupportsChannelID) -> typing.Optional[Channel]:
        channel_id = self.client.channels.to_unique(channel)

        await self.api.delete_channel(channel_id)
        return await self.drop(channel_id)

    def on_create(self) -> OnDecoratorT[ChannelCreateEvent]:
        return self.on(ChannelEvents.CREATE)

    def on_update(self) -> OnDecoratorT[ChannelUpdateEvent]:
        return self.on(ChannelEvents.UPDATE)

    def on_delete(self) -> OnDecoratorT[ChannelDeleteEvent]:
        return self.on(ChannelEvents.DELETE)

    def on_pins_update(self) -> OnDecoratorT[ChannelPinsUpdateEvent]:
        return self.on(ChannelEvents.PINS_UPDATE)

    async def channel_created(self, shard: Shard, data: RawChannelCreate) -> None:
        guild = self.client.guilds.wrap(data.get('guild_id'))

    async def channel_updated(self, shard: Shard, data: RawChannelUpdate) -> None:
        guild = self.client.guilds.wrap(data.get('guild_id'))

    async def channel_deleted(self, shard: Shard, data: RawChannelDelete) -> None:
        guild = self.client.guilds.wrap(data.get('guild_id'))

    async def channel_pins_updated(self, shard: Shard, data: RawChannelPinsUpdate) -> None:
        guild = self.client.guilds.wrap(data.get('guild_id'))


class GuildChannelsView(CachedStateView[SupportsChannelID, Snowflake, Channel]):
    def __init__(
        self,
        *,
        state: ChannelState,
        channels: typing.Iterable[SupportsChannelID],
        guild: SupportsGuildID,
    ) -> None:
        super().__init__(state=state, keys=channels)
        self.guild_id = self.client.guilds.to_unique(guild)

    async def fetch_all(self) -> typing.List[Channel]:
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
