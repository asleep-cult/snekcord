from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from ..objects.message import Message

if TYPE_CHECKING:
    from ..manager import BaseManager
    from ..objects.channel import Channel


class ChannelMessageState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __message_class__ = Message

    def __init__(self, *, manager: BaseManager,
                 channel: Channel) -> None:
        super().__init__(manager=manager)
        self.channel = channel

    @classmethod
    def set_message_class(cls, klass: type) -> None:
        cls.__message_class__ = klass

    def append(self, data: dict, *args, **kwargs) -> Message:
        message = self.get(data['id'])
        if message is not None:
            message._update(data)
        else:
            message = self.__message_class__.unmarshal(
                data, state=self, *args, **kwargs)
            message.cache()

        return message
