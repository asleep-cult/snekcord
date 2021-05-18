from .baseobject import BaseTemplate
from .. import rest
from ..utils import JsonArray, JsonField, JsonObject, JsonTemplate, Snowflake

__all__ = ('GuildWidgetChannel', 'GuildWidgetMember',
           'GuildWidgetJson', 'GuildWidget')

GuildWidgetChannel = JsonTemplate(
    name=JsonField('name'),
    position=JsonField('position'),
    __extends__=(BaseTemplate,)
).default_object('GuildWidgetChannel')


GuildWidgetMember = JsonTemplate(
    username=JsonField('username'),
    discriminator=JsonField('discriminator'),
    avatar=JsonField('avatar'),
    status=JsonField('status'),
    avatar_url=JsonField('avatar_url'),
    __extends__=(BaseTemplate,)
).default_object('GuildWidgetMember')


GuildWidgetJson = JsonTemplate(
    name=JsonField('name'),
    instant_invite=JsonField('instant_invite'),
    channels=JsonArray('channels', object=GuildWidgetChannel),
    members=JsonArray('members', object=GuildWidgetMember),
    presence_count=JsonField('presence_count'),
    __extends__=(BaseTemplate,)
).default_object('GuildWidgetJson')


GuildWidgetSettingsTemplate = JsonTemplate(
    enabled=JsonField('enabled'),
    channel_id=JsonField('channel_id'),
)


class GuildWidget(JsonObject, template=GuildWidgetSettingsTemplate):
    __slots__ = ('guild', 'enabled', 'channel_id')

    def __json_init__(self, *, guild):
        self.guild = guild

    @property
    def channel(self):
        return self.guild.channels.get(self.channel_id)

    async def fetch(self):
        data = await rest.get_guild_widget_settings.request(
            session=self.guild.state.manager.rest,
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
            session=self.guild.state.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            json=json)

        self.update(data)

        return self

    async def fetch_json(self):
        data = await rest.get_guild_widget.request(
            session=self.guild.state.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        return GuildWidgetJson.unmarshal(data)

    async def fetch_shield(self):
        data = await rest.get_guild_widget_image.request(
            session=self.guild.state.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        return data

    async def fetch_banner(self, style='1'):
        style = f'banner{style}'

        data = await rest.get_guild_widget_image.request(
            session=self.guild.state.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            params=dict(style=style))

        return data
