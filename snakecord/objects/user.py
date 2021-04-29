from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseObject
from ..templates.user import UserTemplate

if TYPE_CHECKING:
    from ..states.user import UserState

class User(BaseObject, template=UserTemplate):
    __slots__ = ('_state',)

    def __init__(self, *, state: UserState):
        self._state = state
    
    @property
    def mention(self):
        return f'<@!{self.id}>'
