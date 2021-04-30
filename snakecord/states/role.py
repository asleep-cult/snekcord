from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseState, SnowflakeMapping
from ..objects.role import Role

if TYPE_CHECKING:
    from ..objects.guild import Guild
    from ..clients.user.manager import UserClientManager


class RoleState(BaseState):
    __container__ = SnowflakeMapping
    __role_class__ = Role

    @classmethod
    def set_role_class(cls, klass: type):
        cls.__role_class__ = klass

    def __init__(self, *, manager: UserClientManager, guild: Guild):
        super().__init__(manager=manager)
        self.guild = guild

    def append(self, data: dict, *args, **kwargs):
        role = self.get(data['id'])
        if role is not None:
            role._update(data)
        else:
            role = self.__role_class__.unmarshal(
                data, state=self, guild=self.guild, *args, **kwargs)
            self[role.id] = role

        return role
