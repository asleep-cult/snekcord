from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .guildobject import Guild
from ..flags import Permissions
from ..states.rolestate import RoleState
from ..utils import JsonField, JsonObject, Snowflake


class RoleTags(JsonObject):
    bot_id: t.ClassVar[JsonField[Snowflake]]
    integration_id: t.ClassVar[JsonField[Snowflake]]
    premium_subscriber: t.ClassVar[JsonField[bool]]


class Role(BaseObject[Snowflake]):
    raw_name: t.ClassVar[JsonField[str]]
    color: t.ClassVar[JsonField[int]]
    hoist: t.ClassVar[JsonField[bool]]
    position: t.ClassVar[JsonField[int]]
    permissions: t.ClassVar[JsonField[Permissions]]
    managed: t.ClassVar[JsonField[bool]]
    mentionable: t.ClassVar[JsonField[bool]]
    tags: t.ClassVar[JsonField[RoleTags]]

    state: RoleState

    def __init_(self, *, state: RoleState) -> None: ...

    @property
    def guild(self) -> Guild: ...

    @property
    def name(self) -> str: ...

    @property
    def mention(self) -> str: ...

    async def modify(self, **kwargs: t.Any) -> Role: ...
