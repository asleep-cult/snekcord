from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.memberobject import GuildMember
from ..objects.overwriteobject import (
    PermissionOverwrite, PermissionOverwriteType)
from ..objects.roleobject import Role
from ..utils import Permissions, Snowflake

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import GuildChannel
    from ..typing import Json, SnowflakeType


__all__ = ('PermissionOverwriteState',)


class PermissionOverwriteState(BaseState[Snowflake, PermissionOverwrite]):
    __key_transformer__ = Snowflake.try_snowflake
    __permission_overwrite_class__ = PermissionOverwrite

    def __init__(self, *, client: Client, channel: GuildChannel) -> None:
        super().__init__(client=client)
        self.channel = channel

    @property
    def everyone(self):
        return self.get(self.channel.guild_id)

    def upsert(self, data: Json) -> PermissionOverwrite:  # type: ignore
        overwrite = self.get(data['id'])
        if overwrite is not None:
            overwrite.update(data)
        else:
            overwrite = self.__permission_overwrite_class__.unmarshal(
                data, state=self)
            overwrite.cache()

        return overwrite

    def apply_to(self, member: SnowflakeType) -> t.Optional[Permissions]:
        if not isinstance(member, GuildMember):
            guild = self.channel.guild
            if guild is None:
                return None

            guild_member = guild.members.get(member)
            if guild_member is None:
                return None
        else:
            guild_member = member

        permissions = guild_member.permissions

        if permissions.administrator:
            return permissions

        value = permissions.value

        overwrite = self.everyone
        if overwrite is not None:
            value &= ~overwrite.deny.value
            value |= overwrite.allow.value

        allow = 0
        deny = 0
        for role_id in guild_member.roles.keys():
            overwrite = self.get(role_id)
            if overwrite is not None:
                allow |= overwrite.allow.value
                deny |= overwrite.deny.value

        value &= ~deny
        value |= allow

        overwrite = self.get(member)
        if overwrite is not None:
            value &= ~overwrite.deny.value
            value |= overwrite.allow.value

        return Permissions.from_value(value)

    async def create(self, obj: SnowflakeType, **kwargs: t.Any):
        if isinstance(obj, GuildMember):
            obj_id = obj.id
            kwargs['type'] = PermissionOverwriteType.MEMBER
        if isinstance(obj, Role):
            obj_id = obj.id
            kwargs['type'] = PermissionOverwriteType.ROLE
        else:
            obj_id = Snowflake.try_snowflake(obj)
            kwargs['type'] = PermissionOverwriteType.get_value(
                kwargs['type'])

        try:
            kwargs['allow'] = Permissions.get_value(kwargs['allow'])
        except KeyError:
            pass

        try:
            kwargs['deny'] = Permissions.get_value(kwargs['deny'])
        except KeyError:
            pass

        await rest.create_channel_permission.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.channel.id, overwrite_id=obj_id),
            json=kwargs)
