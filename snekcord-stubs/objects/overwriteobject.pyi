from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .channelobject import GuildChannel
from ..enums import PermissionOverwriteType
from ..flags import Permissions
from ..states.overwritestate import PermissionOverwriteState
from ..utils.json import JsonField
from ..utils.snowflake import Snowflake


class PermissionOverwrie(BaseObject[Snowflake]):
    type: t.ClassVar[JsonField[PermissionOverwriteType]]
    allow: t.ClassVar[JsonField[Permissions]]
    deny: t.ClassVar[JsonField[Permissions]]

    state: PermissionOverwriteState

    def __init__(self, *, state: PermissionOverwriteState) -> None: ...

    @property
    def channel(self) -> GuildChannel: ...

    async def modify(self, **kwargs: t.Any) -> None: ...

    async def delete(self) -> None: ...
