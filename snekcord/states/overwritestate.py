from .basestate import BaseState
from .. import http
from ..flags import Permissions
from ..objects.memberobject import GuildMember
from ..objects.overwriteobject import PermissionOverwrite, PermissionOverwriteType
from ..objects.roleobject import Role
from ..snowflake import Snowflake

__all__ = ('PermissionOverwriteState',)


class PermissionOverwriteState(BaseState):
    def __init__(self, *, client, channel):
        super().__init__(client=client)
        self.channel = channel

    @property
    def everyone(self):
        return self.get(self.channel.guild_id)

    def upsert(self, data):
        overwrite = self.get(Snowflake(data['id']))

        if overwrite is not None:
            overwrite.update(data)
        else:
            overwrite = PermissionOverwrite.unmarshal(data, state=self)
            overwrite.cache()

        return overwrite

    async def create(self, obj, *, allow, deny, type=None):
        json = {}

        obj_id = Snowflake.try_snowflake(obj)

        if type is not None:
            json['type'] = PermissionOverwriteType.try_value(type)

        elif isinstance(obj, GuildMember):
            json['type'] = PermissionOverwriteType.MEMBER

        elif isinstance(obj, Role):
            json['type'] = PermissionOverwriteType.ROLE

        json['allow'] = Permissions.try_value(allow)
        json['deny'] = Permissions.try_value(deny)

        await http.create_channel_permission_overwrite.request(
            self.client.http, channel_id=self.channel.id, overwrite_id=obj_id, json=json
        )

    async def delete(self, overwrite):
        overwrite_id = Snowflake.try_snowflake(overwrite)

        await http.delete_channel_permission_overwrite.request(
            self.client.http, channel_id=self.channel.id, overwrite_id=overwrite_id
        )

    def apply_to(self, member):
        if not isinstance(member, GuildMember):
            if self.channel.guild is None:
                return None

            member = self.channel.guild.members.get(member)

            if member is None:
                return None

        permissions = member.permissions.copy()

        if permissions.administrator:
            return permissions

        if self.everyone is not None:
            permissions.value |= self.everyone.allow.value
            permissions.value &= ~self.everyone.deny.value

        allow = 0
        deny = 0

        for role_id in member.roles.keys():
            overwrite = self.get(role_id)

            if overwrite is not None:
                allow |= overwrite.allow.value
                deny |= overwrite.deny.value

        permissions.value |= allow
        permissions.value &= ~deny

        overwrite = self.get(member)

        if overwrite is not None:
            permissions.value |= permissions.allow.value
            permissions.value &= ~overwrite.deny.value

        return permissions
