from __future__ import annotations

import enum
import typing

import attr

from .base_events import BaseEvent

if typing.TYPE_CHECKING:
    from ..objects import Role
    from ..states import GuildIDWrapper


class RoleEvents(str, enum.Enum):
    CREATE = 'GUILD_ROLE_CREATE'
    UPDATE = 'GUILD_ROLE_UPDATE'
    DELETE = 'GUILD_ROLE_DELETE'


@attr.s(kw_only=True)
class RoleCreateEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    role: Role = attr.ib()


@attr.s(kw_only=True)
class RoleUpdateEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    role: Role = attr.ib()


@attr.s(kw_only=True)
class RoleDeleteEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    role: typing.Optional[Role] = attr.ib()
