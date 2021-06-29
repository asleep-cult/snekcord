from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .guildobject import Guild
from .userobject import User
from ..states.memberstate import GuildMemberState
from ..states.rolestate import GuildMemberRoleState
from ..utils.json import JsonTemplate
from ..utils.permissions import Permissions
from ..utils.snowflake import Snowflake

GuildMemberTemplate: JsonTemplate = ...


class GuildMember(BaseObject[Snowflake], template=GuildMemberTemplate):
    nick: str
    created_at: datetime
    premium_since: datetime
    daef: bool
    mute: bool
    pending: bool

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
