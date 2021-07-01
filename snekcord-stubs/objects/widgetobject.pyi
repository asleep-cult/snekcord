from __future__ import annotations

import typing as t

from .channelobject import GuildChannel
from .guildobject import Guild
from ..typedefs import SnowflakeConvertible
from ..utils import JsonArray, JsonField, JsonObject, Snowflake


class GuildWidgetChannel(JsonObject):
    id: t.ClassVar[JsonField[Snowflake]]
    name: t.ClassVar[JsonField[str]]
    position: t.ClassVar[JsonField[int]]


class GuildWidgetMember(JsonObject):
    id: t.ClassVar[JsonField[Snowflake]]
    username: t.ClassVar[JsonField[str]]
    discriminator: t.ClassVar[JsonField[str]]
    avatar: t.ClassVar[JsonField[str]]
    status: t.ClassVar[JsonField[str]]
    avatar_url: t.ClassVar[JsonField[str]]


class GuildWidgetJson(JsonObject):
    id: t.ClassVar[JsonField[Snowflake]]
    name: t.ClassVar[JsonField[str]]
    instant_invite: t.ClassVar[JsonField[str]]
    channels: t.ClassVar[JsonArray[GuildWidgetChannel]]
    members: t.ClassVar[JsonArray[GuildWidgetMember]]
    presence_count: t.ClassVar[JsonField[int]]


class GuildWidget(JsonObject):
    enabled: t.ClassVar[JsonField[bool]]
    channel_id: t.ClassVar[JsonField[Snowflake]]

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
