from __future__ import annotations

import typing

from ..builders import RoleCreateBuilder, RolePositionsBuilder, RoleUpdateBuilder
from ..cache import RefStore, SnowflakeMemoryRefStore
from ..enums import CacheFlags, Permissions
from ..events import RoleEvents
from ..objects import (
    CachedRole,
    Role,
    SnowflakeWrapper,
    SupportsGuildID,
    SupportsRoleID,
)
from ..rest.endpoints import DELETE_GUILD_ROLE, GET_GUILD_ROLES
from ..snowflake import Snowflake
from ..streams import SupportsStream
from ..undefined import MaybeUndefined, undefined
from .base_state import CachedEventState, CachedStateView

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..json import JSONObject, JSONType

__all__ = ('RoleState', 'GuildRolesView')


class RoleState(CachedEventState[SupportsRoleID, Snowflake, CachedRole, Role]):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.guild_refstore = self.create_guild_refstore()

    def create_guild_refstore(self) -> RefStore[Snowflake, Snowflake]:
        return SnowflakeMemoryRefStore()

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

        roles = await self.guild_refstore.get(guild_id)
        return self.client.create_guild_roles_view(roles, guild_id)

    def inject_metadata(self, data: JSONType, guild_id: Snowflake) -> JSONObject:
        if not isinstance(data, dict):
            raise TypeError('data should be a JSON object')

        return dict(data, guild_id=guild_id)

    async def upsert_cached(
        self, data: JSONObject, flags: CacheFlags = CacheFlags.ALL
    ) -> CachedRole:
        role_id = Snowflake.into(data, 'id')
        assert role_id is not None

        guild_id = Snowflake.into(data, 'guild_id')
        if guild_id is not None and flags & CacheFlags.GUILDS:
            await self.guild_refstore.add(guild_id, role_id)

        async with self.synchronize(role_id):
            cached = await self.cache.get(role_id)

            if cached is None:
                cached = CachedRole.from_json(data)

                if flags & CacheFlags.ROLES:
                    await self.cache.create(role_id, cached)
            else:
                cached.update(data)
                await self.cache.update(role_id, cached)

        return cached

    async def from_cached(self, cached: CachedRole) -> Role:
        return Role(
            client=self.client,
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
            await self.guild_refstore.remove(object.guild_id, object.id)

    async def fetch_all(self, guild: SupportsGuildID) -> typing.List[Role]:
        guild_id = self.client.guilds.to_unique(guild)

        data = await self.client.rest.request_api(GET_GUILD_ROLES, guild_id=guild_id)
        assert isinstance(data, list)

        iterator = (self.inject_metadata(role, guild_id) for role in data)
        return [await self.upsert(role) for role in iterator]

    def create(
        self,
        guild: SupportsGuildID,
        *,
        name: MaybeUndefined[str] = undefined,
        permissions: MaybeUndefined[Permissions] = undefined,
        color: MaybeUndefined[int] = undefined,
        hoist: MaybeUndefined[bool] = undefined,
        icon: MaybeUndefined[SupportsStream] = undefined,
        unicode_emoji: MaybeUndefined[str] = undefined,
        mentionable: MaybeUndefined[bool] = undefined,
    ) -> RoleCreateBuilder:
        builder = RoleCreateBuilder(
            client=self.client, guild_id=self.client.guilds.to_unique(guild)
        )

        return builder.setters(
            name=name,
            permissions=permissions,
            color=color,
            hoist=hoist,
            icon=icon,
            unicode_emoji=unicode_emoji,
            mentionable=mentionable,
        )

    def update(
        self,
        guild: SupportsGuildID,
        role: SupportsRoleID,
        *,
        name: MaybeUndefined[typing.Optional[str]] = undefined,
        permissions: MaybeUndefined[typing.Optional[Permissions]] = undefined,
        color: MaybeUndefined[typing.Optional[int]] = undefined,
        hoist: MaybeUndefined[typing.Optional[bool]] = undefined,
        icon: MaybeUndefined[typing.Optional[SupportsStream]] = undefined,
        unicode_emoji: MaybeUndefined[typing.Optional[str]] = undefined,
        mentionable: MaybeUndefined[typing.Optional[bool]] = undefined,
    ) -> RoleUpdateBuilder:
        builder = RoleUpdateBuilder(
            client=self.client,
            guild_id=self.client.guilds.to_unique(guild),
            role_id=self.to_unique(role),
        )

        return builder.setters(
            name=name,
            permissions=permissions,
            color=color,
            hoist=hoist,
            icon=icon,
            unicode_emoji=unicode_emoji,
            mentionable=mentionable,
        )

    def update_positions(self, guild: SupportsGuildID) -> RolePositionsBuilder:
        return RolePositionsBuilder(
            client=self.client, guild_id=self.client.guilds.to_unique(guild)
        )

    async def delete(self, guild: SupportsGuildID, role: SupportsRoleID) -> typing.Optional[Role]:
        role_id = self.client.roles.to_unique(role)

        await self.client.rest.request_api(
            DELETE_GUILD_ROLE, guild_id=self.client.guilds.to_unique(guild), role_id=role_id
        )
        return await self.client.roles.drop(role_id)


class GuildRolesView(CachedStateView[SupportsRoleID, Snowflake, Role]):
    def __init__(
        self, *, state: RoleState, roles: typing.Iterable[SupportsRoleID], guild: SupportsGuildID
    ) -> None:
        super().__init__(state=state, keys=roles)
        self.guild_id = self.client.guilds.to_unique(guild)

    async def fetch_all(self) -> typing.List[Role]:
        return await self.client.roles.fetch_all(self.guild_id)

    def create(
        self,
        *,
        name: MaybeUndefined[str] = undefined,
        permissions: MaybeUndefined[Permissions] = undefined,
        color: MaybeUndefined[int] = undefined,
        hoist: MaybeUndefined[bool] = undefined,
        icon: MaybeUndefined[SupportsStream] = undefined,
        unicode_emoji: MaybeUndefined[str] = undefined,
        mentionable: MaybeUndefined[bool] = undefined,
    ) -> RoleCreateBuilder:
        return self.client.roles.create(
            self.guild_id,
            name=name,
            permissions=permissions,
            color=color,
            hoist=hoist,
            icon=icon,
            unicode_emoji=unicode_emoji,
            mentionable=mentionable,
        )

    def update(
        self,
        role: SupportsRoleID,
        *,
        name: MaybeUndefined[typing.Optional[str]] = undefined,
        permissions: MaybeUndefined[typing.Optional[Permissions]] = undefined,
        color: MaybeUndefined[typing.Optional[int]] = undefined,
        hoist: MaybeUndefined[typing.Optional[bool]] = undefined,
        icon: MaybeUndefined[typing.Optional[SupportsStream]] = undefined,
        unicode_emoji: MaybeUndefined[typing.Optional[str]] = undefined,
        mentionable: MaybeUndefined[typing.Optional[bool]] = undefined,
    ) -> RoleUpdateBuilder:
        return self.client.roles.update(
            self.guild_id,
            role,
            name=name,
            permissions=permissions,
            color=color,
            hoist=hoist,
            icon=icon,
            unicode_emoji=unicode_emoji,
            mentionable=mentionable,
        )

    def update_positions(self) -> RolePositionsBuilder:
        return self.client.roles.update_positions(self.guild_id)

    async def delete(self, role: SupportsRoleID) -> typing.Optional[Role]:
        return await self.client.roles.delete(self.guild_id, role)
