from __future__ import annotations

import typing

import attr

from .base_builders import AwaitableBuilder, setter
from ..rest.endpoints import (
    CREATE_CHANNEL_MESSAGE,
    UPDATE_CHANNEL_MESSAGE,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Message, MessageFlags
else:
    Message = typing.NewType('Message', typing.Any)

__all__ = ('MessageCreateBuilder', 'MessageUpdateBuilder')


@attr.s(kw_only=True, slots=True)
class MessageCreateBuilder(AwaitableBuilder[Message]):
    client: Client = attr.ib()
    channel_id: Snowflake = attr.ib()

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

        data['channel_id'] = self.channel_id
        return await self.client.messages.upsert(data)

    def get_message(self) -> Message:
        if self.result is None:
            raise RuntimeError('get_message() can only be called after await or async with')

        return self.result


@attr.s(kw_only=True, slots=True)
class MessageUpdateBuilder(AwaitableBuilder[Message]):
    client: Client = attr.ib()
    channel_id: Snowflake = attr.ib()
    message_id: Snowflake = attr.ib()

    @setter
    def content(self, content: MaybeUndefined[typing.Optional[str]]) -> None:
        if content is not undefined:
            self.data['content'] = str(content) if content is not None else None

    @setter
    def flags(self, flags: MaybeUndefined[typing.Optional[MessageFlags]]) -> None:
        if flags is not undefined:
            self.data['flags'] = int(flags) if flags is not None else None

    async def action(self) -> Message:
        data = await self.client.rest.request(
            UPDATE_CHANNEL_MESSAGE,
            channel_id=self.channel_id,
            message_id=self.message_id,
            json=self.data,
        )
        assert isinstance(data, dict)

        data['channel_id'] = self.channel_id
        return await self.client.messages.upsert(data)

    def get_message(self) -> Message:
        if self.result is None:
            raise RuntimeError('get_message() can only be called after await or async with')

        return self.result
