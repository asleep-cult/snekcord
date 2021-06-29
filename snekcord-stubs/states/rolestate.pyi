from __future__ import annotations

import typing as t

from .basestate import BaseState, BaseSubState
from ..clients.client import Client
from ..objects.guildobject import Guild
from ..objects.memberobject import GuildMember
from ..objects.roleobject import Role
from ..typedefs import SnowflakeConvertible
from ..utils.snowflake import Snowflake

__all__ = ('RoleState', 'GuildMemberRoleState')


class GuildRolePosition(t.TypedDict):
    position: int


class RoleState(BaseState[SnowflakeConvertible, Snowflake, Role]):
    guild: Guild

    def __init__(self, *, client: Client, guild: Guild) -> None: ...

    @property
    def everyone(self) -> Role | None: ...

    async def fetch_all(self) -> set[Role]: ...

    async def create(self, **kwargs: t.Any) -> Role: ...

    async def modify_many(self,
                          positions: dict[SnowflakeConvertible,
                                          GuildRolePosition]) -> None: ...


class GuildMemberRoleState(
        BaseSubState[SnowflakeConvertible, Snowflake, Role]):
    superstate: RoleState
    member: GuildMember

    def __init__(self, *, superstate: RoleState, member: GuildMember
                 ) -> None: ...

    async def add(self, role: SnowflakeConvertible) -> None: ...

    async def remove(self, role: SnowflakeConvertible) -> None: ...
