from __future__ import annotations

import typing

from .base_state import CachedEventState, CachedStateView
from ..events import (
    RoleEvents,
)
from ..objects import (
    CachedRole,
    Role,
    SnowflakeWrapper,
)
from ..snowflake import Snowflake
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from .guild_state import SupportsGuildID
    from ..json import JSONObject

__all__ = (
    'SupportsRoleID',
    'RoleIDWrapper',
    'RoleState',
    'GuildRolesView',
)

SupportsRoleID = typing.Union[Snowflake, str, int, Role]
RoleIDWrapper = SnowflakeWrapper[SupportsRoleID, Role]


class RoleState(CachedEventState[SupportsRoleID, Snowflake, CachedRole, Role]):
    @property
    def events(self) -> typing.Tuple[str, ...]:
        return tuple(RoleEvents)

    def to_unique(self, object: SupportsRoleID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, Role):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or Role')

    async def for_guild(self, guild: SupportsGuildID) -> GuildRolesView:
        guild_id = self.client.guilds.to_unique(guild)

        roles = await self.client.guilds.role_refstore.get(guild_id)
        return self.client.create_guild_roles_view(roles, guild_id)

    async def upsert(self, data: JSONObject) -> Role:
        role_id = Snowflake.into(data, 'id')
        assert role_id is not None

        guild_id = Snowflake.into(data, 'guild_id')
        if guild_id is not None:
            await self.client.guilds.role_refstore.add(guild_id, role_id)

        async with self.synchronize(role_id):
            cached = await self.cache.get(role_id)

            if cached is None:
                cached = CachedRole.from_json(data)
                await self.cache.create(role_id, cached)
            else:
                cached.update(data)
                await self.cache.update(role_id, cached)

        return await self.from_cached(cached)

    async def from_cached(self, cached: CachedRole) -> Role:
        return Role(
            state=self,
            id=cached.id,
            guild=SnowflakeWrapper(cached.guild_id, state=self.client.guilds),
            name=cached.name,
            color=cached.color,
            hoist=cached.hoist,
            icon=undefined.nullify(cached.icon),
            unicode_emoji=cached.unicode_emoji,
            position=cached.position,
            permissions=cached.permissions,
            managed=cached.managed,
        )

    async def remove_refs(self, object: CachedRole) -> None:
        if object.guild_id is not None:
            await self.client.guilds.role_refstore.remove(object.guild_id, object.id)


class GuildRolesView(CachedStateView[SupportsRoleID, Snowflake, Role]):
    def __init__(
        self, *, state: RoleState, roles: typing.Iterable[SupportsRoleID], guild: SupportsGuildID
    ) -> None:
        super().__init__(state=state, keys=roles)
        self.guild_id = self.client.guilds.to_unique(guild)
