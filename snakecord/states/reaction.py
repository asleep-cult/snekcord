from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseState, SnowflakeMapping
from ..objects.reaction import Reaction

if TYPE_CHECKING:
    from ..objects.message import Message
    from ..clients.user.manager import UserClientManager


class ReactionState(BaseState):
    __container__ = SnowflakeMapping
    __reaction_class__ = Reaction

    def __init__(self, *, manager: UserClientManager, message: Message):
        super().__init__(manager=manager)
        self.message = message
