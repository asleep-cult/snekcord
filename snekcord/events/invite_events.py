from __future__ import annotations

import enum
import typing

import attr

from .base_events import BaseEvent

if typing.TYPE_CHECKING:
    from ..objects import Invite

__all__ = ('InviteEvents', 'InviteCreateEvent', 'InviteDeleteEvent')


class InviteEvents(str, enum.Enum):
    CREATE = 'INVITE_CREATE'
    DELETE = 'INVITE_DELETE'


@attr.s(kw_only=True)
class InviteCreateEvent(BaseEvent):
    invite: Invite = attr.ib()


class InviteDeleteEvent(BaseEvent):
    invite: Invite = attr.ib()
