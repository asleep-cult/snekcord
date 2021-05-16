from .baseobject import BaseStatelessObject, BaseTemplate
from .. import rest
from ..utils import JsonArray, JsonField, JsonTemplate, Snowflake

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


class GuildWidget(BaseStatelessObject):
    __slots__ = ('enabled', 'channel_id')

    def __init__(self, *, owner):
        super().__init__(owner=owner)
        self.enabled = None
        self.channel_id = None

    @property
    def channel(self):
        return self.owner.channels.get(self.channel_id)

    async def fetch(self):
        data = await rest.get_guild_widget_settings.request(
            session=self.owner.state.manager.rest,
            fmt=dict(guild_id=self.owner.id))

        self._update_settings(data)

        return self

    async def modify(self, enabled=None, channel=None):
        json = {}

        if enabled is not None:
            json['enabled'] = enabled

        if channel is not None:
            json['channel_id'] = Snowflake.try_snowflake(channel)

        data = await rest.modify_guild_widget_settings.request(
            session=self.owner.state.manager.rest,
            fmt=dict(guild_id=self.owner.id),
            json=json)

        self._update_settings(data)

        return self

    async def fetch_json(self):
        data = await rest.get_guild_widget.request(
            session=self.owner.state.manager.rest,
            fmt=dict(guild_id=self.owner.id))

        return GuildWidgetJson.unmarshal(data)

    async def fetch_shield(self):
        data = await rest.get_guild_widget_image.request(
            session=self.owner.state.manager.rest,
            fmt=dict(guild_id=self.owner.id))

        return data

    async def fetch_banner(self, style='1'):
        style = f'banner{style}'

        data = await rest.get_guild_widget_image.request(
            session=self.owner.state.manager.rest,
            fmt=dict(guild_id=self.owner.id),
            params=dict(style=style))

        return data

    def _update_settings(self, data):
        self.enabled = data['enabled']
        self.channel_id = Snowflake.try_snowflake(data['channel_id'])
