from .basestate import BaseState
from .. import rest
from ..objects.memberobject import GuildMember
from ..objects.overwriteobject import (
    PermissionOverwrite, PermissionOverwriteType)
from ..objects.roleobject import Role
from ..utils import Permissions, Snowflake


class PermissionOverwriteState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __permission_overwrite_class__ = PermissionOverwrite

    def __init__(self, *, manager, channel):
        super().__init__(manager=manager)
        self.channel = channel

    def upsert(self, data):
        overwrite = self.get(data['id'])
        if overwrite is not None:
            overwrite.update(data)
        else:
            overwrite = self.__permission_overwrite_class__.unmarshal(
                data, state=self)
            overwrite.cache()

        return overwrite

    async def create(self, obj, **kwargs):
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
            session=self.manager.rest,
            fmt=dict(channel_id=self.channel.id, overwrite_id=obj_id),
            json=kwargs)
