from __future__ import annotations
from snekcord.typing import SnowflakeType

import typing as t

from .baseobject import BaseTemplate
from .. import rest
from ..utils import JsonArray, JsonField, JsonObject, JsonTemplate, Snowflake

__all__ = ('GuildWidgetChannel', 'GuildWidgetMember',
           'GuildWidgetJson', 'GuildWidget')

if t.TYPE_CHECKING:
    from .channelobject import GuildChannel
    from .guildobject import Guild
    from ..typing import Json

GuildWidgetChannelTemplate = JsonTemplate(
    name=JsonField('name'),
    position=JsonField('position'),
    __extends__=(BaseTemplate,)
)


class GuildWidgetChannel(JsonObject, template=GuildWidgetChannelTemplate):
    id: Snowflake
    name: str
    position: int


GuildWidgetMemberTemplate = JsonTemplate(
    username=JsonField('username'),
    discriminator=JsonField('discriminator'),
    avatar=JsonField('avatar'),
    status=JsonField('status'),
    avatar_url=JsonField('avatar_url'),
    __extends__=(BaseTemplate,)
)


class GuildWidgetMember(JsonObject, template=GuildWidgetMemberTemplate):
    id: Snowflake
    username: str
    discriminator: str
    avatar: t.Optional[str]
    status: str
    avatar_url: str


GuildWidgetJsonTemplate = JsonTemplate(
    name=JsonField('name'),
    instant_invite=JsonField('instant_invite'),
    channels=JsonArray('channels', object=GuildWidgetChannel),
    members=JsonArray('members', object=GuildWidgetMember),
    presence_count=JsonField('presence_count'),
    __extends__=(BaseTemplate,)
)


class GuildWidgetJson(JsonObject, template=GuildWidgetJsonTemplate):
    id: Snowflake
    name: str
    instant_invite: str
    channels: t.List[GuildWidgetChannel]


GuildWidgetSettingsTemplate = JsonTemplate(
    enabled=JsonField('enabled'),
    channel_id=JsonField('channel_id'),
)


class GuildWidget(JsonObject, template=GuildWidgetSettingsTemplate):
    __slots__ = ('guild',)

    if t.TYPE_CHECKING:
        enabled: bool
        channel_id: t.Optional[Snowflake]

    def __init__(self, *, guild: Guild) -> None:
        self.guild = guild

    @property
    def channel(self) -> t.Optional[GuildChannel]:
        if self.channel_id is not None:
            return self.guild.channels.get(self.channel_id)
        return None

    async def fetch(self) -> GuildWidget:
        data = await rest.get_guild_widget_settings.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        self.update(data)

        return self

    async def modify(
        self, enabled: t.Optional[bool] = None,
        channel: t.Optional[SnowflakeType] = None
    ) -> GuildWidget:
        json: Json = {}

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

    async def fetch_json(self) -> GuildWidgetJson:
        data = await rest.get_guild_widget.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return GuildWidgetJson.unmarshal(data)

    async def fetch_shield(self) -> bytes:
        data = await rest.get_guild_widget_image.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return data

    async def fetch_banner(
        self, style: str = '1'
    ) -> bytes:
        style = f'banner{style}'

        data = await rest.get_guild_widget_image.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id),
            params=dict(style=style))

        return data
