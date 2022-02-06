from __future__ import annotations

import typing

import attr

from ..cache import CachedModel
from ..objects import SnowflakeObject
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined

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
