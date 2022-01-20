from __future__ import annotations

from typing import TYPE_CHECKING, Union

from .base_state import (
    BaseClientState,
    BaseSubState,
)
from ..builders import JSONBuilder
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
from ..rest.endpoints import (
    CREATE_GUILD_ROLE,
    GET_GUILD_ROLES,
)
from ..snowflake import Snowflake
from ..undefined import (
    MaybeUndefined,
    undefined,
)

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import ShardWebSocket

__all__ = ('RoleUnwrappable', 'RoleState', 'GuildRoleState')

RoleUnwrappable = Union[Snowflake, Role, str, int, ObjectWrapper]


class RoleState(BaseClientState):
    @classmethod
    def unwrap_id(cls, object):
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (int, str)):
            return Snowflake(object)

        if isinstance(object, Role):
            return object.id

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, GuildRoleState):
                return object.id

            raise TypeError('Expected ObjectWrapper created by GuildRoleState')

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


class GuildRoleState(BaseSubState):
    def __init__(self, *, superstate: BaseClientState, guild: Guild) -> None:
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
            await role.update_tags(tags)

        return role

    async def fetch_all(self) -> list[Role]:
        data = await self.client.rest.request(GET_GUILD_ROLES, guild_id=self.guild.id)
        assert isinstance(data, dict)

        return [await self.upsert(role) for role in data]

    async def create(
        self,
        *,
        name: MaybeUndefined[str] = undefined,
        permissions: MaybeUndefined[int] = undefined,
        color: MaybeUndefined[int] = undefined,
        hoist: MaybeUndefined[bool] = undefined,
        icon=undefined,
        emoji: MaybeUndefined[str] = undefined,
        mentionable: MaybeUndefined[bool] = undefined,
    ) -> Role:
        body = JSONBuilder()

        body.str('name', name)
        body.str('permissions', permissions)
        body.int('color', color)
        body.bool('hoist', hoist)
        body.str('icon', icon)
        body.bool('mentionable', mentionable)

        data = await self.client.rest.request(CREATE_GUILD_ROLE, guild_id=self.guild.id, json=body)
        assert isinstance(data, dict)

        return await self.upsert(data)
