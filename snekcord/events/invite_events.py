from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING

from .base_events import BaseEvent

if TYPE_CHECKING:
    from ..json import JSONData
    from ..objects import (
        ObjectWrapper,
        Invite,
    )
    from ..websockets import Shard

__all__ = ('InviteEvents', 'InviteCreateEvent', 'InviteDeleteEvent')


class InviteEvents(str, enum.Enum):
    CREATE = 'INVITE_CREATE'
    DELETE = 'INVITE_DELETE'


class InviteCreateEvent(BaseEvent):
    __slots__ = ('invite',)

    def __init__(self, *, shard: Shard, payload: JSONData, invite: Invite) -> None:
        super().__init__(shard=shard, payload=payload)
        self.invite = invite

    def __repr__(self) -> str:
        return f'<InviteCreateEvent invite={self.invite!r}>'


class InviteDeleteEvent(BaseEvent):
    __slots__ = ('invite',)

    def __init__(self, *, shard: Shard, payload: JSONData, invite: Optional[Invite]) -> None:
        super().__init__(shard=shard, payload=payload)
        self.invite = invite

    @property
    def guild(self) -> ObjectWrapper:
        return self.client.guilds.wrap_id(self.payload.get('guild_id'))

    @property
    def channel(self) -> ObjectWrapper:
        return self.client.channels.wrap_id(self.payload.get('channel_id'))

    def __repr__(self) -> str:
        return f'<InviteDeleteEvent invite={self.invite!r}>'
