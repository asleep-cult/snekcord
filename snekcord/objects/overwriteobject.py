from .baseobject import BaseObject
from .. import rest
from ..enums import PermissionOverwriteType
from ..flags import Permissions
from ..utils import _validate_keys
from ..utils.json import JsonField

__all__ = ('PermissionOverwrite',)


class PermissionOverwrite(BaseObject):
    type = JsonField('type', PermissionOverwriteType.get_enum)
    allow = JsonField('allow', Permissions.from_value)
    deny = JsonField('deny', Permissions.from_value)

    @property
    def channel(self):
        return self.state.channel

    async def modify(self, **kwargs):
        kwargs['type'] = PermissionOverwriteType.get_value(self.type)

        try:
            kwargs['allow'] = Permissions.get_value(kwargs['allow'])
        except KeyError:
            pass

        try:
            kwargs['deny'] = Permissions.get_value(kwargs['deny'])
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), rest.create_channel_permission.json)

        await rest.create_channel_permission.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.channel.id, overwrite_id=self.id),
            json=kwargs)

    async def delete(self):
        await rest.delete_channel_permission.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.channel.id, overwrite_id=self.id))
