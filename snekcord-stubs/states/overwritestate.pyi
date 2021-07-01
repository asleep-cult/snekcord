from __future__ import annotations

import typing as t

from .basestate import BaseState
from ..clients.client import Client
from ..flags import Permissions
from ..objects.channelobject import GuildChannel
from ..objects.overwriteobject import PermissionOverwrie
from ..typedefs import SnowflakeConvertible
from ..utils import Snowflake


class PermissionOverwriteState(BaseState[Snowflake, PermissionOverwrie]):
    channel: GuildChannel

    def __init__(self, *, client: Client, channel: GuildChannel) -> None: ...

    @property
    def everyone(self) -> PermissionOverwrie | None: ...

    def apply_to(self, member: SnowflakeConvertible) -> Permissions | None: ...

    async def create(self, obj: SnowflakeConvertible, **kwargs: t.Any
                     ) -> None: ...
