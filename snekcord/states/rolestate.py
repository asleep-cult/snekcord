from .basestate import BaseState, BaseSubState
from .. import rest
from ..clients.client import ClientClasses
from ..flags import Permissions
from ..utils import Snowflake

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
            self.client.rest, {'guild_id': self.guild.id}
        )

        return [self.upsert(role) for role in data]

    async def create(
        self, *, name=None, permissions=None, color=None, hoist=None, mentionable=None
    ):
        json = {}

        if name is not None:
            json['name'] = str(name)

        if permissions is not None:
            json['permissions'] = Permissions.get_value(permissions)

        if color is not None:
            json['color'] = int(color)

        if hoist is not None:
            json['hoist'] = bool(hoist)

        if mentionable is not None:
            json['mentionable'] = bool(mentionable)

        data = await rest.create_guild_role.request(
            self.client.rest, {'guild_id': self.guild.id}, json=json
        )

        return self.upsert(data)

    async def modify_many(self, roles):
        json = []

        for role, data in roles.items():
            role = {'id': Snowflake.try_snowflake(role)}

            if 'position' in data:
                position = data['position']

                if position is not None:
                    role['position'] = int(position)
                else:
                    role['position'] = None

            json.append(role)

        await rest.modify_guild_roles.request(
            self.client.rest, {'guild_id': self.guild.id}, json=json
        )

    async def delete(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.delete_guild_role.request(
            self.client.rest, {'guild_id': self.guild.id, 'role_id': role_id}
        )


class GuildMemberRoleState(BaseSubState):
    def __init__(self, *, superstate, member):
        super().__init__(superstate=superstate)
        self.member = member

    async def add(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.add_guild_member_role.request(
            self.superstate.client.rest,
            {
                'guild_id': self.member.guild.id,
                'user_id': self.member.id,
                'role_id': role_id
            }
        )

    async def remove(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.remove_guild_member_role.request(
            self.superstate.client.rest,
            {
                'guild_id': self.member.guild.id,
                'user_id': self.member.id,
                'role_id': role_id
            }
        )
