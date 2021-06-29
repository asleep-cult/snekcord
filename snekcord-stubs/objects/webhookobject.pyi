from typing import Any, Literal, Optional, overload

from .baseobject import BaseObject
from .guildobject import Guild
from .messageobject import Message
from ..utils import Enum, JsonTemplate, Snowflake
from ..typedefs import Json, SnowflakeConvertible

class WebhookType(Enum[int]):
    incoming = 1
    channel_follower = 2
    application = 3

WebhookTemplate: JsonTemplate = ...

class Webhook(BaseObject[Snowflake]):
    type: WebhookType
    guild_id: Snowflake | None
    channel_id: Snowflake | None
    _user: Json | None
    name: str
    avatar: str | None
    token: str | None
    application_id: Snowflake | None
    _source_guild: Json | None
    source_channel: Json | None
    url: str | None


    @property
    def guild(self) -> Guild | None:
        ...

    @property
    def channel(self) -> Guild | None:
        ...

    async def modify(
        self, name: str, avatar: Any, channel_id: Snowflake
    ) -> Webhook:
        ...

    async def delete(self) -> None:
        ...

    @overload
    async def execute(
        self, *, wait: Literal[False], thread_id: Snowflake | None = ..., **kwargs: Any
    ) -> None:
        ...

    @overload
    async def execute(
        self, *, wait: bool = ..., thread_id: Snowflake | None = ..., **kwargs: Any
    ) -> Message:
        ...

    async def fetch_message(self, message_id: SnowflakeConvertible) -> Message:
        ...

    async def edit_message(
        self, message_id: SnowflakeConvertible, **kwargs: Any
    ) -> Message:
        ...

    async def delete_message(self, message_id: SnowflakeConvertible) -> None:
        ...
