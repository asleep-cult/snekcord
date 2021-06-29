from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .guildobject import Guild
from ..states.rolestate import RoleState
from ..utils.json import JsonObject, JsonTemplate
from ..utils.permissions import Permissions
from ..utils.snowflake import Snowflake

RoleTagsTemplate: JsonTemplate = ...


class RoleTags(JsonObject, template=RoleTagsTemplate):
    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: bool


RoleTemplate: JsonTemplate = ...


class Role(BaseObject[Snowflake], template=RoleTemplate):
    raw_name: str
    color: int
    hoist: bool
    position: int
    permissions: Permissions
    managed: bool
    mentionable: bool
    tags: RoleTags

    state: RoleState

    def __init_(self, *, state: RoleState) -> None: ...

    @property
    def guild(self) -> Guild: ...

    @property
    def name(self) -> str: ...

    @property
    def mention(self) -> str: ...

    async def modify(self, **kwargs: t.Any) -> Role: ...
