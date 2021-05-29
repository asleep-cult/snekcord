from .basestate import BaseState, BaseSubState
from .. import rest
from ..objects.baseobject import BaseObject
from ..objects.channelobject import (
    ChannelType,
    DMChannel,
    TextChannel,
    VoiceChannel,
    _guild_channel_creation_keys,
)
from ..utils import Snowflake, _validate_keys

__all__ = ('ChannelState',)


class ChannelState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __channel_classes__ = {
        ChannelType.GUILD_TEXT: TextChannel,
        ChannelType.GUILD_VOICE: VoiceChannel,
        ChannelType.DM: DMChannel,
    }
    __default_class__ = BaseObject

    def get_class(self, type):
        return self.__channel_classes__.get(type, self.__default_class__)

    def upsert(self, data):
        channel = self.get(data['id'])
        if channel is not None:
            channel.update(data)
        else:
            channel = self.get_class(data['type']).unmarshal(data, state=self)
            channel.cache()

        return channel

    async def fetch(self, channel):
        channel_id = Snowflake.try_snowflake(channel)

        data = await rest.get_channel.request(
            session=self.manager.rest, fmt=dict(channel_id=channel_id)
        )

        return self.upsert(data)


class GuildChannelState(BaseSubState):
    def __init__(self, *, superstate, guild):
        super().__init__(superstate=superstate)
        self.guild = guild

    @property
    def afk(self):
        return self.get(self.guild.afk_channel_id)

    @property
    def widget(self):
        return self.get(self.guild.widget.channel_id)

    @property
    def application(self):
        return self.get(self.guild.application_channel_id)

    @property
    def system(self):
        return self.get(self.guild.system_channel_id)

    @property
    def rules(self):
        return self.get(self.guild.rules_channel_id)

    @property
    def public_updates(self):
        return self.get(self.guild.public_updates_channel_id)

    async def fetch_all(self):
        data = await rest.get_guild_channels.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.guild.id),
        )

        channels = self.superstate.upsert_many(data)
        self.extend_keys(channel.id for channel in channels)

        return channels

    async def create(self, **kwargs):
        required_keys = ('name',)

        channel_type = kwargs.get('type', 0)
        keys = _guild_channel_creation_keys(channel_type)

        if channel_type in (
            ChannelType.GUILD_TEXT,
            ChannelType.GUILD_NEWS,
            ChannelType.GUILD_STORE,
        ):
            try:
                kwargs['parent_id'] = Snowflake.try_snowflake(
                    kwargs.pop('parent')
                )
            except KeyError:
                pass

        if channel_type == ChannelType.GUILD_TEXT:
            try:
                kwargs['rate_limit_per_user'] = kwargs.pop('slowmode')
            except KeyError:
                pass

        _validate_keys(
            f'{self.__class__.__name__}.create', kwargs, required_keys, keys
        )

        data = await rest.create_guild_channel.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            json=kwargs,
        )

        return self.superstate.upsert(data)

    async def modify_many(self, positions):
        required_keys = ('id',)
        keys = rest.modify_guild_channel_positions.json

        json = []

        for key, value in positions.items():
            value['id'] = Snowflake.try_snowflake(key)

            try:
                value['parent_id'] = Snowflake.try_snowflake(
                    value.pop('parent')
                )
            except KeyError:
                pass

            _validate_keys(f'positions[{key}]', value, required_keys, keys)

            json.append(value)

        await rest.modify_guild_channel_positions.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            json=json,
        )
