from .baseobject import BaseObject
from ..enums import PermissionOverwriteType
from ..flags import Permissions
from ..utils import JsonField, undefined

__all__ = ('PermissionOverwrite',)


class PermissionOverwrite(BaseObject):
    type = JsonField('type', PermissionOverwriteType.get_enum)
    allow = JsonField('allow', Permissions.from_value)
    deny = JsonField('deny', Permissions.from_value)

    @property
    def channel(self):
        return self.state.channel

    @property
    def target(self):
        if self.type == PermissionOverwriteType.MEMBER:
            return self.channel.guild.members.get(self.id)
        elif self.type == PermissionOverwriteType.ROLE:
            return self.channel.guild.roles.get(self.id)

    def modify(self, *, allow=undefined, deny=undefined):
        if allow is not undefined:
            if allow is not None:
                allow = Permissions.get_value(allow)
            else:
                allow = 0

        if deny is not undefined:
            if deny is not None:
                deny = Permissions.get_value(deny)
            else:
                deny = 0

        return self.state.create(self.id, allow=allow, deny=deny, type=self.type)

    def delete(self):
        return self.state.delete(self.id)
