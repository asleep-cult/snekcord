from __future__ import annotations

import typing as t

from .basestate import BaseState
from ..clients.client import Client
from ..objects.channelobject import GuildChannel
from ..objects.overwriteobject import PermissionOverwrie
from ..typedefs import SnowflakeConvertible
from ..utils.permissions import Permissions
from ..utils.snowflake import Snowflake


class PermissionOverwriteState(
        BaseState[SnowflakeConvertible, Snowflake, PermissionOverwrie]):
    channel: GuildChannel

    def __init__(self, *, client: Client, channel: GuildChannel) -> None: ...

    @property
    def everyone(self) -> PermissionOverwrie | None: ...

    def apply_to(self, member: SnowflakeConvertible) -> Permissions | None: ...

    async def create(self, obj: SnowflakeConvertible, **kwargs: t.Any
                     ) -> None: ...
