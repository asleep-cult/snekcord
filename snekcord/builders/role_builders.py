from __future__ import annotations

import typing

import attr

from .base_builders import AwaitableBuilder, setter
from ..permissions import Permissions
from ..rest.endpoints import (
    CREATE_GUILD_ROLE,
    UPDATE_GUILD_ROLE,
    UPDATE_GUILD_ROLE_POSITIONS,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Role, SupportsRoleID
else:
    Role = typing.NewType('Role', typing.Any)

__all__ = (
    'RoleCreateBuilder',
    'RoleUpdateBuilder',
    'RolePositionsBuilder',
)


@attr.s(kw_only=True)
class RoleCreateBuilder(AwaitableBuilder[Role]):
    client: Client = attr.ib()
    guild_id: Snowflake = attr.ib()

    @setter
    def name(self, name: MaybeUndefined[str]) -> None:
        if name is not undefined:
            self.data['name'] = str(name)

    @setter
    def permissions(self, permissions: MaybeUndefined[Permissions]) -> None:
        if permissions is not undefined:
            self.data['permissions'] = int(permissions)

    @setter
    def color(self, color: MaybeUndefined[int]) -> None:
        if color is not undefined:
            self.data['color'] = int(color)

    @setter
    def hoist(self, hoist: MaybeUndefined[bool]) -> None:
        if hoist is not undefined:
            self.data['hoist'] = bool(hoist)

    # TODO: icon

    @setter
    def unicode_emoji(self, unicode_emoji: MaybeUndefined[str]) -> None:
        if unicode_emoji is not undefined:
            self.data['unicode_emoji'] = str(unicode_emoji)

    @setter
    def mentionable(self, mentionable: MaybeUndefined[bool]) -> None:
        if mentionable is not undefined:
            self.data['mentionable'] = bool(mentionable)

    async def action(self) -> Role:
        data = await self.client.rest.request_api(
            CREATE_GUILD_ROLE, guild_id=self.guild_id, json=self.data
        )
        assert isinstance(data, dict)

        data['guild_id'] = self.guild_id
        return await self.client.roles.upsert(data)

    def get_role(self) -> Role:
        if self.result is None:
            raise RuntimeError('get_role() can only be called after await or async with')

        return self.result


@attr.s(kw_only=True)
class RoleUpdateBuilder(AwaitableBuilder[Role]):
    client: Client = attr.ib()
    guild_id: Snowflake = attr.ib()
    role_id: Snowflake = attr.ib()

    @setter
    def name(self, name: MaybeUndefined[typing.Optional[str]]) -> None:
        if name is not undefined:
            self.data['name'] = str(name) if name is not None else None

    @setter
    def permissions(self, permissions: MaybeUndefined[typing.Optional[Permissions]]) -> None:
        if permissions is not undefined:
            self.data['permissions'] = int(permissions) if permissions is not None else None

    @setter
    def color(self, color: MaybeUndefined[typing.Optional[int]]) -> None:
        if color is not undefined:
            self.data['color'] = int(color) if color is not None else None

    @setter
    def hoist(self, hoist: MaybeUndefined[typing.Optional[bool]]) -> None:
        if hoist is not undefined:
            self.data['hoist'] = bool(hoist) if hoist is not None else None

    # TODO: icon

    @setter
    def unicode_emoji(self, unicode_emoji: MaybeUndefined[typing.Optional[str]]) -> None:
        if unicode_emoji is not undefined:
            self.data['unicode_emoji'] = str(unicode_emoji) if unicode_emoji is not None else None

    @setter
    def mentionable(self, mentionable: MaybeUndefined[typing.Optional[bool]]) -> None:
        if mentionable is not undefined:
            self.data['mentionable'] = bool(mentionable) if mentionable is not None else None

    async def action(self) -> Role:
        data = await self.client.rest.request_api(
            UPDATE_GUILD_ROLE, guild_id=self.guild_id, role_id=self.role_id, json=self.data
        )
        assert isinstance(data, dict)

        data['guild_id'] = self.guild_id
        return await self.client.roles.upsert(data)

    def get_role(self) -> Role:
        if self.result is None:
            raise RuntimeError('get_role() can only be called after await or async with')

        return self.result


@attr.s(kw_only=True)
class RolePositionsBuilder(AwaitableBuilder[typing.List[Role]]):
    client: Client = attr.ib()
    guild_id: Snowflake = attr.ib()

    @setter
    def set(self, role: SupportsRoleID, *, position: int) -> None:
        role_id = str(self.client.roles.to_unique(role))
        self.data[role_id] = {'id': role_id, 'position': position}

    async def action(self) -> typing.List[Role]:
        json = list(self.data.values())

        data = await self.client.rest.request_api(
            UPDATE_GUILD_ROLE_POSITIONS, guild_id=self.guild_id, json=json
        )
        assert isinstance(data, list)

        return [await self.client.roles.upsert(role) for role in data]

    def get_roles(self) -> typing.List[Role]:
        if self.result is None:
            raise RuntimeError('get_roles() can only be called after await or async with')

        return self.result
