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
    name: JsonField[str]
    description: JsonField[str]
    usage_count: JsonField[int]
    creator_id: JsonField[Snowflake]
    created_at: JsonField[datetime]
    updated_at: JsonField[datetime]
    source_guild_id: JsonField[Snowflake]
    serialized_source_guild: JsonField[Json]
    is_dirty: JsonField[bool]

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
