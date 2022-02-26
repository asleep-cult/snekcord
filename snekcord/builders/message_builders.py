from __future__ import annotations

import typing

import attr

from ..rest.endpoints import CREATE_CHANNEL_MESSAGE, UPDATE_CHANNEL_MESSAGE
from ..snowflake import Snowflake
from .base_builders import AwaitableBuilder, setter

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Message, MessageFlags

__all__ = ('MessageCreateBuilder', 'MessageUpdateBuilder')


@attr.s(kw_only=True, slots=True)
class MessageCreateBuilder(AwaitableBuilder):
    client: Client = attr.ib()
    channel_id: Snowflake = attr.ib()

    @setter
    def content(self, content: str) -> None:
        self.data['content'] = str(content)

    @setter
    def tts(self, tts: bool) -> None:
        self.data['tts'] = bool(tts)

    @setter
    def flags(self, flags: MessageFlags) -> None:
        self.data['flags'] = int(flags)

    async def action(self) -> Message:
        data = await self.client.rest.request_api(
            CREATE_CHANNEL_MESSAGE, channel_id=self.channel_id, json=self.data
        )
        assert isinstance(data, dict)

        return await self.client.messages.upsert(
            self.client.messages.inject_metadata(data, self.channel_id)
        )

    def get_message(self) -> Message:
        if self.result is None:
            raise RuntimeError('get_message() can only be called after await or async with')

        return self.result


@attr.s(kw_only=True, slots=True)
class MessageUpdateBuilder(AwaitableBuilder):
    client: Client = attr.ib()
    channel_id: Snowflake = attr.ib()
    message_id: Snowflake = attr.ib()

    @setter
    def content(self, content: typing.Optional[str]) -> None:
        self.data['content'] = str(content) if content is not None else None

    @setter
    def flags(self, flags: typing.Optional[MessageFlags]) -> None:
        self.data['flags'] = int(flags) if flags is not None else None

    async def action(self) -> Message:
        data = await self.client.rest.request_api(
            UPDATE_CHANNEL_MESSAGE,
            channel_id=self.channel_id,
            message_id=self.message_id,
            json=self.data,
        )
        assert isinstance(data, dict)

        return await self.client.messages.upsert(
            self.client.messages.inject_metadata(data, self.channel_id)
        )

    def get_message(self) -> Message:
        if self.result is None:
            raise RuntimeError('get_message() can only be called after await or async with')

        return self.result
