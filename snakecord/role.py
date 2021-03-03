from .bases import BaseObject, BaseState
from .utils import JsonStructure, JsonField, Snowflake

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .guild import Guild


class RoleTags(JsonStructure):
    __slots__ = ('bot_id', 'integration_id', 'premium_subscriber')

    __json_fields__ = {
        'bot_id': JsonField('bot_id', Snowflake, str),
        'integration_id': JsonField('integration_id', Snowflake, str),
        'premium_subscriber': JsonField('premium_subscriber'),
    }

    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: bool


class Role(BaseObject):
    __slots__ = (
        'id', 'name', 'color', 'hoist', 'position', 'permissions', 'managed',
        'mentionable', 'tags'
    )

    __json_fields__ = {
        'name': JsonField('name'),
        'color': JsonField('color'),
        'hoist': JsonField('hoist'),
        'position': JsonField('position'),
        'permissions': JsonField('permissions'),
        'managed': JsonField('managed'),
        'mentionable': JsonField('mentionable'),
        'tags': JsonField('tags', struct=RoleTags),
    }

    id: Snowflake
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: RoleTags

    def __init__(self, state, guild):
        self._state = state
        self.guild: 'Guild' = guild

    async def edit(
        self,
        *,
        name=None,
        permissions=None,
        color=None,
        hoist=None,
        mentionable=None
    ):
        rest = self._state._client.rest
        resp = await rest.modify_guild_role(
            self.guild.id, self.id, name=name,
            permission=permissions, color=color,
            hoist=hoist, mentionable=mentionable
        )
        data = await resp.json()
        role = self._state._add(data)
        return role

    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_guild_role(
            self.guild.id, self.id
        )


class RoleState(BaseState):
    __state_class__ = Role

    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data):
        role = self.get(data['id'])
        if role is not None:
            role._update(data)
            return role
        role = self.__state_class__.unmarshal(
            data,
            state=self,
            guild=self._guild
        )
        self._values[role.id] = role
        return role

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_guild_roles(self._guild.id)
        data = await resp.json()
        roles = []
        for role in data:
            role = self._add(role)
            roles.append(role)
        return roles

    async def create(
        self,
        *,
        name=None,
        permissions=None,
        color=None,
        hoist=None,
        mentionable=None
    ):
        rest = self._client.rest
        resp = await rest.create_guild_role(
            self._guild.id, name=name, permission=permissions,
            color=color, hoist=hoist, mentionable=mentionable
        )
        data = await resp.json()
        role = self._add(data)
        return role

    async def modify_postions(self, positions):
        rest = self._client.rest
        resp = await rest.modify_guild_role_permissions(
            self._guild.id,
            positions
        )
        data = await resp.json()
        roles = []
        for role in data:
            role = self._add(role)
            roles.append(role)
        return roles
