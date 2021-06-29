from __future__ import annotations

from .channelobject import GuildChannel
from .guildobject import Guild
from ..typedefs import SnowflakeConvertible
from ..utils.json import JsonObject, JsonTemplate
from ..utils.snowflake import Snowflake

GuildWidgetChannelTemplate: JsonTemplate = ...


class GuildWidgetChannel(JsonObject, template=GuildWidgetChannelTemplate):
    id: Snowflake
    name: str
    position: int


GuildWidgetMemberTemplate: JsonTemplate = ...


class GuildWidgetMember(JsonObject, template=GuildWidgetMemberTemplate):
    id: Snowflake
    username: str
    discriminator: str
    avatar: str
    status: str
    avatar_url: str


GuildWidgetJsonTemplate: JsonTemplate = ...


class GuildWidgetJson(JsonObject, template=GuildWidgetJsonTemplate):
    id: Snowflake
    name: str
    instant_invite: str
    channels: list[GuildWidgetChannel]
    members: list[GuildWidgetMember]
    presence_count: int


GuildWidgetSettingsTemplate: JsonTemplate = ...


class GuildWidget(JsonObject, template=GuildWidgetSettingsTemplate):
    enabled: bool
    channel_id: Snowflake

    guild: Guild

    def __init__(self, *, guild: Guild) -> None: ...

    @property
    def channel(self) -> GuildChannel | None: ...

    async def fetch(self) -> GuildWidget: ...

    async def modify(self, enabled: bool | None = ...,
                     channel: SnowflakeConvertible | None = ...
                     ) -> GuildWidget: ...

    async def fetch_json(self) -> GuildWidgetJson: ...

    async def fetch_shield(self) -> bytes: ...

    async def fetch_banner(self, style: str = ...) -> bytes: ...
