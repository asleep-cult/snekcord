from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING, Type, Union

from .base import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from ..connections import rest
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
    def set_message_class(cls, klass: Type[Message]) -> None:
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

    def create(
        self,
        content: Optional[str] = None,
        *,
        nonce: Optional[Union[int, str]] = None,
        tts: bool = False,
        embed: Optional[dict] = None,
        allowed_mentions: Optional[dict] = None,
        message_reference: Optional[dict] = None
    ) -> rest.RestFuture[Message]:
        payload: Dict[str, Any] = {'tts': tts}

        if content is not None:
            payload['content'] = content

        if nonce is not None:
            payload['nonce'] = nonce
        
        if embed is not None:
            payload['embed'] = embed
        
        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions
        
        if message_reference is not None:
            payload['message_reference'] = message_reference

        return rest.create_channel_message.request(
            session=self.manager.rest,
            fmt={'channel_id': self.channel.id}, json=payload
        )