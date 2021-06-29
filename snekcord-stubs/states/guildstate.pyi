import typing as t

from .basestate import BaseState
from ..clients.client import Client
from ..objects.guildobject import Guild, GuildBan
from ..objects.templateobject import GuildTemplate
from ..typedefs import Json, SnowflakeConvertible
from ..utils.snowflake import Snowflake


class GuildState(BaseState[SnowflakeConvertible, Snowflake, Guild]):
    def new_template(self, data: Json) -> GuildTemplate: ...

    def new_template_many(self, values: list[Json]) -> set[GuildTemplate]: ...

    async def fetch(self, guild: SnowflakeConvertible, *,
                    with_counts: bool | None = ...,
                    sync: bool = ...) -> Guild: ...

    async def fetch_many(self, before: SnowflakeConvertible | None = ...,
                         after: SnowflakeConvertible | None = ...,
                         limit: SnowflakeConvertible | None = ...
                         ) -> set[Guild]: ...

    async def fetch_preview(self, guild: SnowflakeConvertible) -> None: ...

    async def fetch_template(self, code: str) -> GuildTemplate: ...

    async def create(self, **kwargs: t.Any) -> Guild: ...


class GuildBanState(BaseState[SnowflakeConvertible, Snowflake, GuildBan]):
    guild: Guild

    def __init__(self, *, client: Client, guild: Guild) -> None: ...

    async def fetch(self, ban: SnowflakeConvertible) -> GuildBan: ...

    async def fetch_all(self) -> set[GuildBan]: ...

    async def add(self, user: SnowflakeConvertible,
                  **kwargs: t.Any) -> None: ...

    async def remove(self, user: SnowflakeConvertible) -> None: ...
