from .. import rest
from ..fetchables import GuildWidgetImage
from ..utils import JsonArray, JsonField, JsonObject, Snowflake, undefined

__all__ = ('GuildWidgetChannel', 'GuildWidgetMember', 'GuildWidgetJson', 'GuildWidget')


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

    @property
    def image(self):
        return GuildWidgetImage(
            rest=self.guild.state.client.rest, guild_id=self.guild.id
        )

    async def fetch(self):
        data = await rest.get_guild_widget.request(
            self.guild.state.client.rest, {'guild_id': self.guild.id}
        )

        return self.update(data)

    async def modify(self, *, enabled=None, channel=undefined):
        json = {}

        if enabled is not None:
            json['enabled'] = enabled

        if channel is not undefined:
            if channel is not None:
                json['channel_id'] = Snowflake.try_snowflake(channel)
            else:
                json['channel_id'] = None

        data = await rest.modify_guild_widget_settings.request(
            self.guild.state.client.rest,
            {'guild_id': self.guild.id},
            json=json
        )

        return self.update(data)
