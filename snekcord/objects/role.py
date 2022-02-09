from __future__ import annotations

import typing

import attr

from ..builders import RoleUpdateBuilder
from ..cache import CachedModel
from ..objects import SnowflakeObject
from ..permissions import Permissions
from ..rest.endpoints import DELETE_GUILD_ROLE
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

if typing.TYPE_CHECKING:
    from ..states import (
        RoleState,
        GuildIDWrapper,
        SupportsRoleID,
    )
else:
    SupportsRoleID = typing.NewType('SupportsRoleID', typing.Any)


class CachedRoleTags(typing.TypedDict, total=False):
    bot_id: str
    integration_id: str
    premium_subscriber: None


class CachedRole(CachedModel):
    id: Snowflake
    guild_id: typing.Optional[Snowflake]
    name: str
    color: int
    hoist: bool
    icon: typing.Optional[MaybeUndefined[str]]
    unicode_emoji: typing.Optional[str]
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: MaybeUndefined[CachedRoleTags]


@attr.s(kw_only=True, slots=True, hash=True)
class Role(SnowflakeObject[SupportsRoleID]):
    state: RoleState

    guild: GuildIDWrapper = attr.ib(eq=False)
    name: str = attr.ib(eq=False)
    color: int = attr.ib(repr=False, eq=False)
    hoist: bool = attr.ib(eq=False)
    icon: typing.Optional[str] = attr.ib(repr=False, eq=False)
    unicode_emoji: typing.Optional[str] = attr.ib(eq=False)
    position: int = attr.ib(eq=False)
    permissions: str = attr.ib(repr=False, eq=False)
    managed: bool = attr.ib(eq=False)
    # tags

    def update(
        self,
        *,
        name: MaybeUndefined[typing.Optional[str]] = undefined,
        permissions: MaybeUndefined[typing.Optional[Permissions]] = undefined,
        color: MaybeUndefined[typing.Optional[int]] = undefined,
        hoist: MaybeUndefined[typing.Optional[bool]] = undefined,
        unicode_emoji: MaybeUndefined[typing.Optional[str]] = undefined,
        mentionable: MaybeUndefined[typing.Optional[bool]] = undefined,
    ) -> RoleUpdateBuilder:
        builder = RoleUpdateBuilder(
            client=self.client, guild_id=self.guild.unwrap_id(), role_id=self.id
        )

        builder.name(name)
        builder.permissions(permissions)
        builder.color(color)
        builder.hoist(hoist)
        builder.unicode_emoji(unicode_emoji)
        builder.mentionable(mentionable)

        return builder

    async def delete(self) -> typing.Optional[Role]:
        await self.client.rest.request(
            DELETE_GUILD_ROLE, guild_id=self.guild.unwrap_id(), role_id=self.id
        )
        return await self.client.roles.drop(self.id)
