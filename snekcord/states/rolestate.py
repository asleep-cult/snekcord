from .basestate import BaseState, BaseSubState
from .. import rest
from ..clients.client import ClientClasses
from ..utils import Snowflake, _validate_keys

__all__ = ('RoleState', 'GuildMemberRoleState')


class RoleState(BaseState):
    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    @property
    def everyone(self):
        return self.get(self.guild.id)

    def upsert(self, data):
        role = self.get(Snowflake(data['id']))

        if role is not None:
            role.update(data)
        else:
            role = ClientClasses.Role.unmarshal(data, state=self)
            role.cache()

        return role

    async def fetch_all(self):
        data = await rest.get_guild_roles.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id))

        roles = []

        for role in data:
            roles.append(self.upsert(role).id)

        return roles

    async def create(self, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, (), rest.create_guild_role.json)

        data = await rest.create_guild_role.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id),
            json=kwargs)

        return self.upsert(data)

    async def modify_many(self, positions):
        json = []

        for key, value in positions.items():
            value['id'] = Snowflake.try_snowflake(key)

            _validate_keys(f'positions[{key}]',
                           value, ('id',),
                           rest.modify_guild_role_positions.json)

            json.append(value)

        await rest.modify_guild_role_positions.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id),
            json=json)


class GuildMemberRoleState(BaseSubState):
    def __init__(self, *, superstate, member):
        super().__init__(superstate=superstate)
        self.member = member

    async def add(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.add_guild_member_role.request(
            session=self.superstate.client.rest,
            fmt=dict(guild_id=self.member.guild.id,
                     user_id=self.member.user.id,
                     role_id=role_id))

    async def remove(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.remove_guild_member_role.request(
            session=self.superstate.client.rest,
            fmt=dict(guild_id=self.member.guild.id,
                     user_id=self.member.user.id,
                     role_id=role_id))
