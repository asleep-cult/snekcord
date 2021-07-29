from .basestate import BaseState, BaseSubState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.channelobject import ChannelType
from ..snowflake import Snowflake

__all__ = ('ChannelState', 'GuildChannelState')


class ChannelState(BaseState):
    def get_class(self, type):
        if type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS):
            return ClientClasses.TextChannel
        elif type == ChannelType.DM:
            return ClientClasses.DMChannel
        elif type == ChannelType.GUILD_VOICE:
            return ClientClasses.VoiceChannel
        elif type == ChannelType.GUILD_STAGE_VOICE:
            return ClientClasses.StageChannel
        elif type == ChannelType.GUILD_CATEGORY:
            return ClientClasses.CategoryChannel
        elif type == ChannelType.GUILD_STORE:
            return ClientClasses.StorChannel
        else:
            return ClientClasses.GuildChannel

    def upsert(self, data):
        channel = self.get(Snowflake(data['id']))

        if channel is not None:
            channel.update(data)
        else:
            channel = self.get_class(data.get('type')).unmarshal(data, state=self)
            channel.cache()

        return channel

    async def fetch(self, channel):
        channel_id = Snowflake.try_snowflake(channel)

        data = await rest.get_channel.request(
            self.client.rest, channel_id=channel_id,
        )

        return self.upsert(data)

    async def delete(self, channel):
        channel_id = Snowflake.try_snowflake(channel)

        await rest.delete_channel.request(self.client.rest, channel_id=channel_id)

    async def close(self, channel):
        return self.delete(channel)


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

    def upsert(self, data):
        channel = self.superstate.upsert(data)
        channel._json_data_['guild_id'] = self.guild._json_data_['id']

        self.add_key(channel.id)

        return channel

    async def fetch_all(self):
        data = await rest.get_guild_channels.request(
            self.superstate.client.rest, guild_id=self.guild.id
        )

        return [self.upsert(channel) for channel in data]

    async def modify_many(self, channels):
        json = []

        for channel, data in channels.items():
            channel = {'channel': Snowflake.try_snowflake(channel)}

            if 'position' in data:
                position = data['position']

                if position is not None:
                    channel['position'] = position
                else:
                    channel['position'] = None

            if 'lock_permissions' in data:
                lock_permissions = data['lock_permissions']

                if lock_permissions is not None:
                    channel['lock_permissions'] = bool(lock_permissions)
                else:
                    channel['lock_permissions'] = None

            if 'parent' in data:
                parent = data['parent']

                if parent is not None:
                    channel['parent'] = Snowflake.try_snowflake(parent)
                else:
                    channel['parent'] = None

            json.append(channel)

        await rest.modify_guild_channels.request(
            self.superstate.client.rest, guild_id=self.guild.id, json=json
        )
