from __future__ import annotations

import typing as t

from .basestate import BaseState
from ..clients.client import Client
from ..objects.guildobject import Guild
from ..objects.memberobject import GuildMember
from ..typedefs import SnowflakeConvertible
from ..utils.snowflake import Snowflake

__all__ = ('GuildMemberState',)


class GuildMemberState(
        BaseState[SnowflakeConvertible, Snowflake, GuildMember]):
    guild: Guild

    def __init__(self, *, client: Client, guild: Guild) -> None: ...

    async def fetch(self, user: SnowflakeConvertible) -> GuildMember: ...

    async def fetch_many(self, around: Snowflake | None = ...,
                         before: Snowflake | None = ...,
                         after: Snowflake | None = ...,
                         limit: int | None = ...) -> set[GuildMember]: ...

    async def search(self, query: str,
                     limit: int | None) -> list[GuildMember]: ...

    async def add(self, user: SnowflakeConvertible,
                  **kwargs: t.Any) -> GuildMember: ...

    async def remove(self, user: SnowflakeConvertible) -> None: ...
