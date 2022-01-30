from __future__ import annotations

import typing

import attr

from ..cache import CachedModel
from ..objects import SnowflakeObject
from ..undefined import MaybeUndefined

if typing.TYPE_CHECKING:
    from ..states import (
        RoleState,
        SupportsRoleID,
    )
else:
    SupportsRoleID = typing.NewType('SupportsRoleID', typing.NewType)


class CachedRoleTags(typing.TypedDict, total=False):
    bot_id: str
    integration_id: str
    premium_subscriber: None


class CachedRole(CachedModel):
    name: str
    color: int
    hoist: bool
    icon: typing.Optional[MaybeUndefined[str]]
    unicode_emoji: typing.Optional[str]
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: CachedRoleTags


@attr.s(kw_only=True)
class Role(SnowflakeObject[SupportsRoleID]):
    state: RoleState

    name: str = attr.ib()
    color: int = attr.ib()
    hoist: bool = attr.ib()
    icon: typing.Optional[str] = attr.ib()
    unicode_emoji: typing.Optional[str] = attr.ib()
    position: int = attr.ib()
    permissions: str = attr.ib()
    managed: bool = attr.ib()
    # tags
