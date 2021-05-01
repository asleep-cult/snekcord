from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseObject
from ..templates.reaction import ReactionTemplate

if TYPE_CHECKING:
    from .message import Message


class Reaction(BaseObject, template=ReactionTemplate):
    __slots__ = ('message',)

    def __init__(self, *, state, message: Message):
        super().__init__(state=state)
        self.message = message
