from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .guildobject import Guild
from .userobject import User
from ..flags import Permissions
from ..states.memberstate import GuildMemberState
from ..states.rolestate import GuildMemberRoleState
from ..utils.json import JsonField
from ..utils.snowflake import Snowflake


class GuildMember(BaseObject[Snowflake]):
    nick: t.ClassVar[JsonField[str]]
    created_at: t.ClassVar[JsonField[datetime]]
    premium_since: t.ClassVar[JsonField[datetime]]
    daef: t.ClassVar[JsonField[bool]]
    mute: t.ClassVar[JsonField[bool]]
    pending: t.ClassVar[JsonField[bool]]

    state: GuildMemberState
    user: User | None
    roles: GuildMemberRoleState

    @property
    def guild(self) -> Guild: ...

    @property
    def permissions(self) -> Permissions: ...

    @property
    def mention(self) -> str: ...

    @property
    def removed(self) -> bool: ...

    @property
    def removed_at(self) -> datetime: ...

    async def modify(self, **kwargs: t.Any) -> GuildMember: ...
