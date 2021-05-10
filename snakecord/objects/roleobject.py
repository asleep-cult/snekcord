from .baseobject import BaseObject
from ..templates import RoleTemplate


class Role(BaseObject, template=RoleTemplate):
    def __init__(self, *, state, guild):
        super().__init__(state)
        self.guild = guild
