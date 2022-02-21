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
from ..streams import SupportsStream, create_stream

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Role
    from ..states import SupportsRoleID
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
    def name(self, name: str) -> None:
        self.data['name'] = str(name)

    @setter
    def permissions(self, permissions: Permissions) -> None:
        self.data['permissions'] = int(permissions)

    @setter
    def color(self, color: int) -> None:
        self.data['color'] = int(color)

    @setter
    def hoist(self, hoist: bool) -> None:
        self.data['hoist'] = bool(hoist)

    @setter
    def icon(self, icon: SupportsStream) -> None:
        self.data['icon'] = create_stream(icon)

    @setter
    def unicode_emoji(self, unicode_emoji: str) -> None:
        self.data['unicode_emoji'] = str(unicode_emoji)

    @setter
    def mentionable(self, mentionable: bool) -> None:
        self.data['mentionable'] = bool(mentionable)

    async def action(self) -> Role:
        icon = self.data.get('icon')
        if icon is not None:
            if icon is not None:
                self.data['icon'] = await icon.to_data_uri()
            else:
                self.data['icon'] = None

        data = await self.client.rest.request_api(
            CREATE_GUILD_ROLE, guild_id=self.guild_id, json=self.data
        )
        assert isinstance(data, dict)

        return await self.client.roles.upsert(
            self.client.roles.inject_metadata(data, self.guild_id)
        )

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
    def name(self, name: typing.Optional[str]) -> None:
        self.data['name'] = str(name) if name is not None else None

    @setter
    def permissions(self, permissions: typing.Optional[Permissions]) -> None:
        self.data['permissions'] = int(permissions) if permissions is not None else None

    @setter
    def color(self, color: typing.Optional[int]) -> None:
        self.data['color'] = int(color) if color is not None else None

    @setter
    def hoist(self, hoist: typing.Optional[bool]) -> None:
        self.data['hoist'] = bool(hoist) if hoist is not None else None

    @setter
    def icon(self, icon: typing.Optional[SupportsStream]) -> None:
        self.data['icon'] = create_stream(icon) if icon is not None else None

    @setter
    def unicode_emoji(self, unicode_emoji: typing.Optional[str]) -> None:
        self.data['unicode_emoji'] = str(unicode_emoji) if unicode_emoji is not None else None

    @setter
    def mentionable(self, mentionable: typing.Optional[bool]) -> None:
        self.data['mentionable'] = bool(mentionable) if mentionable is not None else None

    async def action(self) -> Role:
        icon = self.data.get('icon')
        if icon is not None:
            self.data['icon'] = await icon.to_data_uri()

        data = await self.client.rest.request_api(
            UPDATE_GUILD_ROLE, guild_id=self.guild_id, role_id=self.role_id, json=self.data
        )
        assert isinstance(data, dict)

        return await self.client.roles.upsert(
            self.client.roles.inject_metadata(data, self.guild_id)
        )

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

        iterator = (self.client.roles.inject_metadata(role, self.guild_id) for role in data)
        return [await self.client.roles.upsert(role) for role in iterator]

    def get_roles(self) -> typing.List[Role]:
        if self.result is None:
            raise RuntimeError('get_roles() can only be called after await or async with')

        return self.result
