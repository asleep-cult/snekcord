from .basestate import (BaseState, BaseSubState, SnowflakeMapping,
                        WeakValueSnowflakeMapping)
from .. import rest
from ..objects.roleobject import Role
from ..utils import Snowflake


class RoleState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __guild_class__ = Role

    def __init__(self, *, manager, guild):
        super().__init__(manager=manager)
        self.guild = guild


class GuildMemberRoleState(BaseSubState):
    def __init__(self, *, superstate, member):
        super().__init__(superstate=superstate)
        self.member = member

    async def add(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.add_guild_member_role.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.member.guild.id,
                     user_id=self.member.user.id,
                     role_id=role_id))

    async def remove(self, role):
        role_id = Snowflake.try_snowflake(role)

        await rest.remove_guild_member_role.request(
            session=self.superstate.manager.rest,
            fmt=dict(guild_id=self.member.guild.id,
                     user_id=self.member.user.id,
                     role_id=role_id))
