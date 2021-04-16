from .obj import BaseObject
from ..templates.guild import GuildTemplate


class Guild(BaseObject, template=GuildTemplate):
    __slots__ = ('_state',)

    def __init__(self, *, state) -> None:
        self._state = state
