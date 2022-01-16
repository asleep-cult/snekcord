from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from .base_events import BaseEvent

if TYPE_CHECKING:
    from ..json import JSONData
    from ..objects import (
        ObjectWrapper,
        Role,
    )
    from ..websockets import ShardWebSocket


class RoleEvent(str, enum.Enum):
    CREATE = 'GUILD_ROLE_CREATE'
    UPDATE = 'GUILD_ROLE_UPDATE'
    DELETE = 'GUILD_ROLE_DELETE'


class RoleCreateEvent(BaseEvent):
    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, role: Role) -> None:
        super().__init__(shard=shard, payload=payload)
        self.role = role

    @staticmethod
    def get_type() -> RoleEvent:
        return RoleEvent.CREATE

    def __repr__(self) -> str:
        return f'<RoleCreateEvent role={self.role!r}>'

    @property
    def guild(self) -> ObjectWrapper:
        return self.client.guilds.wrap_id(self.payload.get('guild_id'))


class RoleUpdateEvent(BaseEvent):
    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, role: Role) -> None:
        super().__init__(shard=shard, payload=payload)
        self.role = role

    @staticmethod
    def get_type() -> RoleEvent:
        return RoleEvent.UPDATE

    def __repr__(self) -> str:
        return f'<RoleUpdateEvent role={self.role!r}>'

    @property
    def guild(self) -> ObjectWrapper:
        return self.client.guilds.wrap_id(self.payload.get('guild_id'))


class RoleDeleteEvent(BaseEvent):
    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, role: Role) -> None:
        super().__init__(shard=shard, payload=payload)
        self.role = role

    @staticmethod
    def get_type() -> RoleEvent:
        return RoleEvent.DELETE

    def __repr__(self) -> str:
        return f'<RoleDeleteEvent role={self.role!r}>'

    @property
    def guild(self) -> ObjectWrapper:
        return self.client.guilds.wrap_id(self.payload.get('guild_id'))
