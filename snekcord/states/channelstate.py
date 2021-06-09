from __future__ import annotations

import typing as t

from .basestate import BaseState, BaseSubState
from .. import rest
from ..objects.channelobject import (
    GuildChannel, CategoryChannel, ChannelType, DMChannel, TextChannel,
    VoiceChannel, _guild_channel_creation_keys)
from ..utils import Snowflake, _validate_keys

__all__ = ('ChannelState',)

if t.TYPE_CHECKING:
    from ..objects import Guild
    from ..typing import Json, SnowflakeType

    class Positions(t.TypedDict):
        position: int
        lock_permissions: bool
        parent_id: SnowflakeType


_Channel = t.Union[DMChannel, GuildChannel]


class ChannelState(BaseState[Snowflake, _Channel]):
    __key_transformer__ = Snowflake.try_snowflake
    __channel_classes__: t.Dict[int, t.Type[_Channel]] = {
        ChannelType.GUILD_TEXT: TextChannel,
        ChannelType.DM: DMChannel,
        ChannelType.GUILD_VOICE: VoiceChannel,
        ChannelType.GUILD_CATEGORY: CategoryChannel,
        ChannelType.GUILD_NEWS: TextChannel,
    }
    __default_class__ = GuildChannel

    def get_class(self, type: int) -> t.Type[_Channel]:
        return self.__channel_classes__.get(type, self.__default_class__)

    def upsert(self, data: Json) -> _Channel:  # type: ignore
        channel = self.get(data['id'])
        if channel is not None:
            channel.update(data)
        else:
            channel = self.get_class(data['type']).unmarshal(data, state=self)
            channel.cache()

        return channel

    async def fetch(self, obj: SnowflakeType) -> _Channel:  # type: ignore
        channel_id = Snowflake.try_snowflake(obj)

        data = await rest.get_channel.request(
            session=self.client.rest,
            fmt=dict(channel_id=channel_id))

        return self.upsert(data)


class GuildChannelState(BaseSubState[Snowflake, GuildChannel]):
    if t.TYPE_CHECKING:
        superstate: ChannelState  # type: ignore
        guild: Guild

    def __init__(self, *, superstate: ChannelState, guild: Guild) -> None:
        super().__init__(superstate=superstate)  # type: ignore
        self.guild = guild

    @property
    def afk(self) -> VoiceChannel:
        return self.get(self.guild.afk_channel_id)  # type: ignore

    @property
    def widget(self) -> GuildChannel:
        return self.get(self.guild.widget.channel_id)  # type: ignore

    @property
    def application(self) -> GuildChannel:
        return self.get(self.guild.application_channel_id)  # type: ignore

    @property
    def system(self) -> TextChannel:
        return self.get(self.guild.system_channel_id)  # type: ignore

    @property
    def rules(self) -> TextChannel:
        return self.get(self.guild.rules_channel_id)  # type: ignore

    @property
    def public_updates(self) -> TextChannel:
        return self.get(self.guild.public_updates_channel_id)  # type: ignore

    async def fetch_all(self) -> t.Set[GuildChannel]:
        data = await rest.get_guild_channels.request(
            session=self.superstate.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.superstate.upsert_many(data)  # type: ignore

    async def create(self, **kwargs: t.Any) -> GuildChannel:
        required_keys = ('name',)

        channel_type = kwargs.get('type', 0)
        keys = _guild_channel_creation_keys(channel_type)  # type: ignore

        if channel_type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS,
                            ChannelType.GUILD_STORE):
            try:
                kwargs['parent_id'] = Snowflake.try_snowflake(
                    kwargs.pop('parent'))
            except KeyError:
                pass

        if channel_type == ChannelType.GUILD_TEXT:
            try:
                kwargs['rate_limit_per_user'] = kwargs.pop('slowmode')
            except KeyError:
                pass

        _validate_keys(f'{self.__class__.__name__}.create',  # type: ignore
                       kwargs, required_keys, keys)

        data = await rest.create_guild_channel.request(
            session=self.superstate.client.rest,
            fmt=dict(guild_id=self.guild.id),
            json=kwargs)

        return self.superstate.upsert(data)  # type: ignore

    async def modify_many(self, positions: t.Dict[SnowflakeType, Positions]):
        json: t.List[t.Dict[str, t.Any]] = []

        for key, value in positions.items():
            value['id'] = Snowflake.try_snowflake(key)  # type: ignore

            try:
                value['parent_id'] = Snowflake.try_snowflake(
                    value.pop('parent'))
            except KeyError:
                pass

            _validate_keys(f'positions[{key}]', value, ('id',),  # type: ignore
                           rest.modify_guild_channel_positions.json)

            json.append(dict(value))  # type: ignore

        await rest.modify_guild_channel_positions.request(
            session=self.superstate.client.rest,
            fmt=dict(guild_id=self.guild.id),
            json=json)
