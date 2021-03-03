from . import structures
from .state import BaseState


class Role(structures.Role):
    __slots__ = (
        'id', 'name', 'color', 'hoist', 'position', 'permissions', 'managed',
        'mentionable', 'tags'
    )

    def __init__(self, state, guild):
        self._state = state
        self.guild = guild

    async def edit(self, **kwargs):
        rest = self._state.client.rest
        data = await rest.modify_guild_role(self.guild.id, self.id, **kwargs)
        role = self._state._add(data)
        return role

    async def delete(self):
        rest = self._state.client.rest
        await rest.delete_guild_role(self.guild.id, self.id)


class RoleState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self.guild = guild

    def _add(self, data):
        role = self.get(data['id'])
        if role is not None:
            role._update(data)
            return role

        role = Role.unmarshal(data, state=self, guild=self.guild)
        self._items[role.id] = role
        return role

    async def fetch_all(self):
        rest = self.client.rest
        data = await rest.get_guild_roles(self.guild.id)
        roles = [self._add(role) for role in data]
        return roles

    async def create(self, **kwargs):
        rest = self.client.rest
        data = await rest.create_guild_role(self.guild.id, **kwargs)
        role = self._add(data)
        return role

    async def modify_postions(self, positions):
        rest = self.client.rest
        data = await rest.modify_guild_role_permissions(self.guild.id, positions)
        roles = [self._add(role) for role in data]
        return roles
