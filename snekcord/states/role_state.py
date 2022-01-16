from __future__ import annotations

from typing import TYPE_CHECKING

from .base_state import (
    BaseState,
    BaseSubsidiaryState,
)
from ..events import (
    BaseEvent,
    RoleCreateEvent,
    RoleDeleteEvent,
    RoleEvent,
    RoleUpdateEvent,
)
from ..intents import WebSocketIntents
from ..objects import (
    Guild,
    ObjectWrapper,
    Role,
)
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import ShardWebSocket

__all__ = ('RoleState', 'GuildRoleState')


class RoleState(BaseState):
    @classmethod
    def unwrap_id(cls, object):
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (int, str)):
            return Snowflake(object)

        if isinstance(object, Role):
            return object.id

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, cls):
                return object.id

            raise TypeError('Expected ObjectWrapper created by RoleState')

        raise TypeError('Expectes Snowflake, int, str, Role or ObjectWrapper')

    def on_create(self):
        return self.on(RoleEvent.CREATE)

    def on_update(self):
        return self.on(RoleEvent.UPDATE)

    def on_delete(self):
        return self.on(RoleEvent.DELETE)

    def get_events(self) -> type[RoleEvent]:
        return RoleEvent

    def get_intents(self) -> WebSocketIntents:
        return WebSocketIntents.GUILDS

    async def process_event(
        self, event: str, shard: ShardWebSocket, payload: JSONData
    ) -> BaseEvent:
        event = self.cast_event(event)

        if event is RoleEvent.CREATE:
            guild = self.client.guilds.get(payload['guild_id'])
            if guild is not None:
                role = await guild.roles.upsert(payload['role'])
            else:
                role = None

            return RoleCreateEvent(shard=shard, payload=payload, role=role)

        if event is RoleEvent.UPDATE:
            guild = self.client.guilds.get(payload['guild_id'])
            if guild is not None:
                role = await guild.roles.upsert(payload['role'])
            else:
                role = None

            return RoleUpdateEvent(shard=shard, payload=payload, role=role)

        if event is RoleEvent.DELETE:
            guild = self.client.guilds.get(payload['guild_id'])
            if guild is not None:
                role = guild.roles.pop(payload['role_id'])
            else:
                role = None

            return RoleDeleteEvent(shard=shard, payload=payload, role=role)


class GuildRoleState(BaseSubsidiaryState):
    def __init__(self, *, superstate: BaseState, guild: Guild) -> None:
        super().__init__(superstate=superstate)
        self.guild = guild

    async def upsert(self, data):
        role = self.get(data['id'])
        if role is not None:
            role.update(data)
        else:
            role = Role.unmarshal(data, state=self)

        tags = data.get('tags')
        if tags is not None:
            role._update_tags(tags)

        return role
