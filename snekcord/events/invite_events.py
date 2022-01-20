from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING

from .base_events import BaseEvent

if TYPE_CHECKING:
    from ..json import JSONData
    from ..objects import Invite
    from ..websockets import ShardWebSocket

__all__ = ('InviteEvent', 'InviteCreateEvent', 'InviteDeleteEvent')


class InviteEvent(str, enum.Enum):
    CREATE = 'INVITE_CREATE'
    DELETE = 'INVITE_DELETE'


class InviteCreateEvent(BaseEvent):
    __slots__ = ('invite',)

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, invite: Invite) -> None:
        super().__init__(shard=shard, payload=payload)
        self.invite = invite

    def __repr__(self) -> str:
        return f'<InviteCreateEvent invite={self.invite!r}>'


class InviteDeleteEvent(BaseEvent):
    __slots__ = ('invite',)

    def __init__(
        self, *, shard: ShardWebSocket, payload: JSONData, invite: Optional[Invite]
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.invite = invite

    def __repr__(self) -> str:
        return f'<InviteDeleteEvent invite={self.invite!r}>'
