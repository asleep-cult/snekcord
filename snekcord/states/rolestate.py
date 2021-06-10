from __future__ import annotations

import typing as t

from .basestate import BaseState, BaseSubState
from .. import rest
from ..objects.roleobject import Role
from ..utils import Snowflake, _validate_keys

__all__ = ('RoleState', 'GuildMemberRoleState')

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Guild, GuildMember
    from ..typing import Json, SnowflakeType

    Positions = t.Dict[SnowflakeType, t.Dict[str, int]]


class RoleState(BaseState[Snowflake, Role]):
    __key_transformer__ = Snowflake.try_snowflake
    __role_class__ = Role

    if t.TYPE_CHECKING:
        guild: Guild

    def __init__(self, *, client: Client, guild: Guild) -> None:
        super().__init__(client=client)
        self.guild = guild

    @property
    def everyone(self) -> t.Optional[Role]:
        return self.get(self.guild.id)

    def upsert(self, data: Json) -> Role:  # type: ignore
        role = self.get(data['id'])
        if role is not None:
            role.update(data)
        else:
            role = self.__role_class__.unmarshal(
                data, state=self)
            role.cache()

        return role

    async def fetch_all(self) -> t.Set[Role]:
        data = await rest.get_guild_roles.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.upsert_many(data)

    async def create(self, **kwargs: t.Any) -> Role:
        _validate_keys(f'{self.__class__.__name__}.create',  # type: ignore
                       kwargs, (), rest.create_guild_role.json)

        data = await rest.create_guild_role.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id),
            json=kwargs)

        return self.upsert(data)

    async def modify_many(self, positions: Positions) -> None:
        json: t.List[t.Dict[str, int]] = []

        for key, value in positions.items():
            value['id'] = Snowflake.try_snowflake(key)

            _validate_keys(f'positions[{key}]',  # type: ignore
                           value, ('id',),
                           rest.modify_guild_role_positions.json)

            json.append(value)

        await rest.modify_guild_role_positions.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id),
            json=json)


class GuildMemberRoleState(BaseSubState[Snowflake, Role]):
    if t.TYPE_CHECKING:
        superstate: RoleState
        member: GuildMember

    def __init__(self, *, superstate: RoleState, member: GuildMember) -> None:
        super().__init__(superstate=superstate)
        self.member = member

    async def add(self, role: SnowflakeType) -> None:
        role_id = Snowflake.try_snowflake(role)

        await rest.add_guild_member_role.request(
            session=self.superstate.client.rest,
            fmt=dict(guild_id=self.member.guild.id,
                     user_id=self.member.user.id,
                     role_id=role_id))

    async def remove(self, role: SnowflakeType) -> None:
        role_id = Snowflake.try_snowflake(role)

        await rest.remove_guild_member_role.request(
            session=self.superstate.client.rest,
            fmt=dict(guild_id=self.member.guild.id,
                     user_id=self.member.user.id,
                     role_id=role_id))
