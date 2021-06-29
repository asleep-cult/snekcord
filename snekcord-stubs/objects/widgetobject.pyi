from __future__ import annotations

from .channelobject import GuildChannel
from .guildobject import Guild
from ..typedefs import SnowflakeConvertible
from ..utils.json import JsonArray, JsonField, JsonObject
from ..utils.snowflake import Snowflake


class GuildWidgetChannel(JsonObject):
    id: JsonField[Snowflake]
    name: JsonField[str]
    position: JsonField[int]


class GuildWidgetMember(JsonObject):
    id: JsonField[Snowflake]
    username: JsonField[str]
    discriminator: JsonField[str]
    avatar: JsonField[str]
    status: JsonField[str]
    avatar_url: JsonField[str]


class GuildWidgetJson(JsonObject):
    id: JsonField[Snowflake]
    name: str
    instant_invite: str
    channels: JsonArray[GuildWidgetChannel]
    members: JsonArray[GuildWidgetMember]
    presence_count: int


class GuildWidget(JsonObject):
    enabled: JsonField[bool]
    channel_id: JsonField[Snowflake]

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
