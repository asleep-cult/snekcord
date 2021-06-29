from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .guildobject import Guild
from ..states.guildstate import GuildState
from ..typedefs import Json
from ..utils.json import JsonField
from ..utils.snowflake import Snowflake


class GuildTemplate(BaseObject[str]):
    name: t.ClassVar[JsonField[str]]
    description: t.ClassVar[JsonField[str]]
    usage_count: t.ClassVar[JsonField[int]]
    creator_id: t.ClassVar[JsonField[Snowflake]]
    created_at: t.ClassVar[JsonField[datetime]]
    updated_at: t.ClassVar[JsonField[datetime]]
    source_guild_id: t.ClassVar[JsonField[Snowflake]]
    serialized_source_guild: t.ClassVar[JsonField[Json]]
    is_dirty: t.ClassVar[JsonField[bool]]

    state: GuildState

    def __init__(self, *, state: GuildState) -> None: ...

    @property
    def code(self) -> str: ...

    @property
    def source_guild(self) -> Guild | None: ...

    async def fetch(self) -> GuildTemplate: ...

    async def create_guild(self, **kwargs: t.Any) -> Guild: ...

    async def sync(self) -> None: ...

    async def modify(self, **kwargs: t.Any) -> GuildTemplate: ...

    async def delete(self) -> None: ...
