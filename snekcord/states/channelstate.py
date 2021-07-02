from .basestate import BaseState, BaseSubState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.channelobject import ChannelType
from ..utils import Snowflake

__all__ = ('ChannelState', 'GuildChannelState')


class ChannelState(BaseState):
    def get_class(self, type):
        if type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS):
            return ClientClasses.TextChannel
        elif type == ChannelType.DM:
            return ClientClasses.DMChannel
        elif type == ChannelType.GUILD_VOICE:
            return ClientClasses.VoiceChannel
        elif type == ChannelType.GUILD_CATEGORY:
            return ClientClasses.CategoryChannel
        else:
            return ClientClasses.GuildChannel

    def upsert(self, data):
        channel = self.get(Snowflake(data['id']))

        if channel is not None:
            channel.update(data)
        else:
            channel = self.get_class(data['type']).unmarshal(data, state=self)
            channel.cache()

        return channel

    async def fetch(self, channel):
        channel_id = Snowflake.try_snowflake(channel)

        data = await rest.get_channel.request(
            self.client.rest, dict(channel_id=channel_id),
        )

        return self.upsert(data)

    async def delete(self, channel):
        channel_id = Snowflake.try_snowflake(channel)

        await rest.delete_channel.request(
            self.client.rest, dict(channel_id=channel_id)
        )

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
