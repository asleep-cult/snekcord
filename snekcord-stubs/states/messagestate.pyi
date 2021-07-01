from __future__ import annotations

import typing as t

from .basestate import BaseState
from ..clients.client import Client
from ..objects.messageobject import Message
from ..typedefs import Channel, SnowflakeConvertible
from ..utils import Snowflake

__all__ = ('MessageState',)


class MessageState(BaseState[Snowflake, Message]):
    channel: Channel

    def __init__(self, *, client: Client, channel: Channel) -> None: ...

    async def fetch(self, message: SnowflakeConvertible) -> Message: ...

    async def fetch_many(self, around: Snowflake | None = ...,
                         before: Snowflake | None = ...,
                         after: Snowflake | None = ...,
                         limit: int | None = ...) -> list[Message]: ...

    async def create(self, **kwargs: t.Any) -> Message: ...

    async def bulk_delete(self, messages: t.Iterable[SnowflakeConvertible]) -> None: ...
