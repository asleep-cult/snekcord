from .. import rest
from ..utils.json import JsonArray, JsonField, JsonObject
from ..utils.snowflake import Snowflake

__all__ = ('GuildWidgetChannel', 'GuildWidgetMember', 'GuildWidgetJson',
           'GuildWidget')


class GuildWidgetChannel(JsonObject):
    id = JsonField('id', Snowflake)
    name = JsonField('name')
    position = JsonField('position')


class GuildWidgetMember(JsonObject):
    id = JsonField('id', Snowflake)
    username = JsonField('username')
    discriminator = JsonField('discriminator')
    avatar = JsonField('avatar')
    status = JsonField('status')
    avatar_url = JsonField('avatar_url')


class GuildWidgetJson(JsonObject):
    id = JsonField('id', Snowflake)
    name = JsonField('name')
    instant_invite = JsonField('instant_invite')
    channels = JsonArray('channels', object=GuildWidgetChannel)
    members = JsonArray('members', object=GuildWidgetMember)
    presence_count = JsonField('presence_count')


class GuildWidget(JsonObject):
    __slots__ = ('guild',)

    enabled = JsonField('enabled')
    channel_id = JsonField('channel_id')

    def __init__(self, *, guild):
        self.guild = guild

    @property
    def channel(self):
        return self.guild.channels.get(self.channel_id)

    async def fetch(self):
        data = await rest.get_guild_widget_settings.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        self.update(data)

        return self

    async def modify(self, enabled=None, channel=None):
        json = {}

        if enabled is not None:
            json['enabled'] = enabled

        if channel is not None:
            json['channel_id'] = Snowflake.try_snowflake(channel)

        data = await rest.modify_guild_widget_settings.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id),
            json=json)

        self.update(data)

        return self

    async def fetch_json(self):
        data = await rest.get_guild_widget.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return GuildWidgetJson.unmarshal(data)

    async def fetch_shield(self):
        data = await rest.get_guild_widget_image.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return data

    async def fetch_banner(self, style='1'):
        style = f'banner{style}'

        data = await rest.get_guild_widget_image.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id),
            params=dict(style=style))

        return data
