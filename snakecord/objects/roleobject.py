from .baseobject import BaseObject
from .. import rest
from ..templates import RoleTemplate
from ..utils import _validate_keys


class Role(BaseObject, template=RoleTemplate):
    __slots__ = ('guild',)

    def __init__(self, *, state, guild):
        super().__init__(state)
        self.guild = guild

    async def modify(self, **kwargs):
        keys = rest.modify_guild_role_positions.json

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild_role_positions.request(
            session=self._state.manager.rest,
            fmt=dict(guild_id=self.guild.id, role_id=self.id),
            json=kwargs)

        return self._state.append(data)

    async def delete(self):
        await rest.delete_guild_role.request(
            session=self._state.manager.rest,
            fmt=dict(guild_id=self.guild.id, role_id=self.id))
