import typing
from datetime import datetime

from .base_state import CachedEventState, CachedStateView
from ..enum import convert_enum
from ..objects import (
    CachedMessage,
    Message,
    MessageFlags,
    MessageType,
    SnowflakeWrapper,
)
from ..snowflake import Snowflake
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from .channel_state import SupportsChannelID
    from ..json import JSONObject

__all__ = (
    'SupportsMessageID',
    'MessageIDWrapper',
    'MessageState',
    'ChannelMessagesView',
)

SupportsMessageID = typing.Union[Snowflake, str, int, Message]
MessageIDWrapper = SnowflakeWrapper[SupportsMessageID, Message]


class MessageState(CachedEventState[SupportsMessageID, Snowflake, CachedMessage, Message]):
    def to_unique(self, object: SupportsMessageID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, Message):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or Message')

    async def upsert(self, data: JSONObject) -> Message:
        message_id = Snowflake(data['id'])
        author = data['author']

        data['author_id'] = author['id']
        await self.client.users.upsert(author)

        async with self.synchronize(message_id):
            cached = await self.cache.get(message_id)

            if cached is None:
                cached = CachedMessage.from_json(data)
                await self.cache.create(message_id, cached)
            else:
                cached.update(data)
                await self.cache.update(message_id, cached)

        return self.from_cached(cached)

    def from_cached(self, cached: CachedMessage) -> Message:
        emited_timestamp = cached.edited_timestamp
        if emited_timestamp is not None:
            emited_timestamp = datetime.fromisoformat(emited_timestamp)

        guild_id = undefined.nullify(cached.guild_id)
        author_id = undefined.nullify(cached.author_id)

        return Message(
            state=self,
            id=Snowflake(cached.id),
            channel=SnowflakeWrapper(cached.channel_id, state=self.client.channels),
            guild=SnowflakeWrapper(guild_id, state=self.client.guilds),
            author=SnowflakeWrapper(author_id, state=self.client.users),
            content=cached.content,
            timestamp=datetime.fromisoformat(cached.timestamp),
            edited_timestamp=emited_timestamp,
            tts=cached.tts,
            nonce=undefined.nullify(cached.nonce),
            pinned=cached.pinned,
            type=convert_enum(MessageType, cached.type),
            flags=MessageFlags(cached.flags),
        )


class ChannelMessagesView(CachedStateView[SupportsMessageID, Snowflake, Message]):
    def __init__(
        self,
        *,
        state: MessageState,
        messages: typing.Iterable[SupportsMessageID],
        channel: SupportsChannelID,
    ) -> None:
        super().__init__(state=state, keys=messages)
        self.channel_id = self.client.channels.to_unique(channel)
