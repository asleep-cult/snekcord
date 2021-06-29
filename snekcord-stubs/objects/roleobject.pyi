from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .guildobject import Guild
from ..states.rolestate import RoleState
from ..utils.json import JsonField, JsonObject
from ..utils.permissions import Permissions
from ..utils.snowflake import Snowflake


class RoleTags(JsonObject):
    bot_id: JsonField[Snowflake]
    integration_id: JsonField[Snowflake]
    premium_subscriber: JsonField[bool]


class Role(BaseObject[Snowflake]):
    raw_name: JsonField[str]
    color: JsonField[int]
    hoist: JsonField[bool]
    position: JsonField[int]
    permissions: JsonField[Permissions]
    managed: JsonField[bool]
    mentionable: JsonField[bool]
    tags: JsonField[RoleTags]

    state: RoleState

    def __init_(self, *, state: RoleState) -> None: ...

    @property
    def guild(self) -> Guild: ...

    @property
    def name(self) -> str: ...

    @property
    def mention(self) -> str: ...

    async def modify(self, **kwargs: t.Any) -> Role: ...
