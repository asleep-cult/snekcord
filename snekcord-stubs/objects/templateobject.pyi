from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .guildobject import Guild
from ..states.guildstate import GuildState
from ..typedefs import Json
from ..utils.json import JsonTemplate
from ..utils.snowflake import Snowflake

GuildTemplateTemplate: JsonTemplate = ...


class GuildTemplate(BaseObject[str], template=GuildTemplateTemplate):
    name: str
    description: str
    usage_count: int
    creator_id: Snowflake
    created_at: datetime
    updated_at: datetime
    source_guild_id: Snowflake
    serialized_source_guild: Json
    is_dirty: bool

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
