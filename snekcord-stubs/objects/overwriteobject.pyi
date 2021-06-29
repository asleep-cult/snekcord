from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .channelobject import GuildChannel
from ..states.overwritestate import PermissionOverwriteState
from ..utils.enum import Enum
from ..utils.json import JsonTemplate
from ..utils.permissions import Permissions
from ..utils.snowflake import Snowflake


class PermissionOverwriteType(Enum[int]):
    ROLE = 0
    MEMBER = 1


PermissionOverwriteTemplate: JsonTemplate = ...


class PermissionOverwrie(BaseObject[Snowflake],
                         template=PermissionOverwriteTemplate):
    type: PermissionOverwriteType
    allow: Permissions
    deny: Permissions

    state: PermissionOverwriteState

    def __init__(self, *, state: PermissionOverwriteState) -> None: ...

    @property
    def channel(self) -> GuildChannel: ...

    async def modify(self, **kwargs: t.Any) -> None: ...

    async def delete(self) -> None: ...
