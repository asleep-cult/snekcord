from __future__ import annotations

import typing

from .base_builders import AwaitableBuilder, setter
from ..rest.endpoints import CREATE_CHANNEL_MESSAGE
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Message, MessageFlags
else:
    Message = typing.NewType('Message', typing.Any)

__all__ = ('MessageCreateBuilder',)


class MessageCreateBuilder(AwaitableBuilder[Message]):
    __slots__ = ('client', 'channel_id')

    def __init__(self, *, client: Client, channel_id: Snowflake) -> None:
        super().__init__()
        self.client = client
        self.channel_id = channel_id

    @setter
    def content(self, content: MaybeUndefined[str]) -> None:
        if content is not undefined:
            self.data['content'] = str(content)

    @setter
    def tts(self, tts: MaybeUndefined[bool]) -> None:
        if tts is not undefined:
            self.data['tts'] = bool(tts)

    @setter
    def flags(self, flags: MaybeUndefined[MessageFlags]) -> None:
        if flags is not undefined:
            self.data['flags'] = int(flags)

    async def action(self) -> Message:
        data = await self.client.rest.request(
            CREATE_CHANNEL_MESSAGE, channel_id=self.channel_id, json=self.data
        )
        assert isinstance(data, dict)

        return await self.client.messages.upsert(data)
