from .basestate import (BaseState, BaseSubState, SnowflakeMapping,
                        WeakValueSnowflakeMapping)
from .. import rest
from ..objects.baseobject import BaseObject
from ..objects.channelobject import (ChannelType, DMChannel, GuildChannel,
                                     TextChannel, VoiceChannel,
                                     _guild_channel_creation_keys)
from ..utils import Snowflake, _validate_keys


class ChannelState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __channel_classes__ = {
        ChannelType.GUILD_TEXT: TextChannel,
        ChannelType.GUILD_VOICE: VoiceChannel,
        ChannelType.DM: DMChannel
    }
    __default_class__ = BaseObject

    def append(self, data):
        channel = self.get(data['id'])
        if channel is not None:
            channel.update(data)
        else:
            Class = self.__channel_classes__.get(
                data['type'], self.__default_class__)
            channel = Class.unmarshal(data, state=self)
            channel.cache()

        return channel

    async def fetch(self, channel_id):
        channel_id = Snowflake.try_snowflake(channel_id)
        data = await rest.get_channel.request(
            session=self.manager.rest,
            fmt=dict(channel_id=channel_id))

        return self.append(data)


class GuildChannelState(BaseSubState):
    def __init__(self, *, superstate, guild):
        super().__init__(superstate=superstate)
        self.guild = guild

    @property
    def afk(self):
        return self.get(self.guild.afk_channel_id)

    @property
    def widget(self):
        return self.get(self.guild.widget_channel_id)

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

    def __key_for__(self, item):
        if isinstance(item, GuildChannel):
            return item.id

    async def fetch(self):
        data = await rest.get_guild_channels.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.superstate.extend(data)

    async def create(self, **kwargs):
        required_keys = ('name',)

        channel_type = kwargs.get('type', 0)
        keys = _guild_channel_creation_keys(channel_type)

        if channel_type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS,
                            ChannelType.GUILD_STORE):
            try:
                kwargs['parent_id'] = (
                    Snowflake.try_snowflake(kwargs.pop('parent'))
                )
            except KeyError:
                pass

        if channel_type is ChannelType.GUILD_TEXT:
            try:
                kwargs['rate_limit_per_user'] = kwargs.pop('slowmode')
            except KeyError:
                pass

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, required_keys, keys)

        data = await rest.create_guild_channel.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            json=kwargs)

        return self.superstate.append(data)

    async def modify_positions(self, positions):
        required_keys = ('id',)

        keys = rest.modify_guild_channel_positions.json

        json = []

        for key, value in positions.items():
            value['id'] = Snowflake.try_snowflake(key)

            try:
                value['parent_id'] = (
                    Snowflake.try_snowflake(value.pop('parent'))
                )
            except KeyError:
                pass

            _validate_keys(f'positions[{key}]', value, required_keys, keys)

            json.append(value)

        await rest.modify_guild_channel_positions.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            json=json)
