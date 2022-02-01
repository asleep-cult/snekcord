from __future__ import annotations

import typing
from datetime import datetime

from .base_state import (
    CachedEventState,
    CachedStateView,
    OnDecoratorT,
)
from ..enum import convert_enum
from ..events import (
    BaseEvent,
    MessageBulkDeleteEvent,
    MessageCreateEvent,
    MessageDeleteEvent,
    MessageEvents,
    MessageUpdateEvent,
)
from ..objects import (
    CachedMessage,
    Message,
    MessageFlags,
    MessageType,
    SnowflakeWrapper,
)
from ..rest.endpoints import (
    CREATE_CHANNEL_MESSAGE,
)
from ..snowflake import Snowflake
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from .channel_state import SupportsChannelID
    from ..json import JSONObject
    from ..websockets import Shard

__all__ = (
    'SupportsMessageID',
    'MessageIDWrapper',
    'MessageState',
    'ChannelMessagesView',
)

SupportsMessageID = typing.Union[Snowflake, str, int, Message]
MessageIDWrapper = SnowflakeWrapper[SupportsMessageID, Message]


class MessageState(CachedEventState[SupportsMessageID, Snowflake, CachedMessage, Message]):
    @property
    def events(self) -> typing.Tuple[str, ...]:
        return tuple(MessageEvents)

    def to_unique(self, object: SupportsMessageID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, Message):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or Message')

    async def upsert(self, data: JSONObject) -> Message:
        message_id = Snowflake.into(data, 'id')
        assert message_id is not None

        channel_id = Snowflake.into(data, 'channel_id')
        if channel_id is not None:
            await self.client.channels.message_refstore.add(channel_id, message_id)

        author = data.get('author')
        if author is not None:
            data['author_id'] = Snowflake(author['id'])
            await self.client.users.upsert(author)

        async with self.synchronize(message_id):
            cached = await self.cache.get(message_id)

            if cached is None:
                cached = CachedMessage.from_json(data)
                await self.cache.create(message_id, cached)
            else:
                cached.update(data)
                await self.cache.update(message_id, cached)

        return await self.from_cached(cached)

    async def from_cached(self, cached: CachedMessage) -> Message:
        emited_timestamp = cached.edited_timestamp
        if emited_timestamp is not None:
            emited_timestamp = datetime.fromisoformat(emited_timestamp)

        guild_id = undefined.nullify(cached.guild_id)
        author_id = undefined.nullify(cached.author_id)

        if cached.flags is not undefined:
            flags = MessageFlags(cached.flags)
        else:
            flags = MessageFlags.NONE

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
            flags=flags,
        )

    async def remove_refs(self, object: CachedMessage) -> None:
        if object.channel_id is not None:
            await self.client.channels.message_refstore.remove(object.channel_id, object.id)

    def on_create(self) -> OnDecoratorT[MessageCreateEvent]:
        return self.on(MessageEvents.CREATE)

    def on_update(self) -> OnDecoratorT[MessageUpdateEvent]:
        return self.on(MessageEvents.UPDATE)

    def on_delete(self) -> OnDecoratorT[MessageDeleteEvent]:
        return self.on(MessageEvents.DELETE)

    def on_bulk_delete(self) -> OnDecoratorT[MessageBulkDeleteEvent]:
        return self.on(MessageEvents.BULK_DELETE)

    async def create_event(self, event: str, shard: Shard, payload: JSONObject) -> BaseEvent:
        event = MessageEvents(event)

        guild = SnowflakeWrapper(payload.get('guild_id'), state=self.client.guilds)
        channel = SnowflakeWrapper(payload.get('channel_id'), state=self.client.channels)

        if event is MessageEvents.CREATE:
            message = await self.upsert(payload)
            return MessageCreateEvent(
                shard=shard, payload=payload, guild=guild, channel=channel, message=message
            )

        elif event is MessageEvents.UPDATE:
            message = await self.upsert(payload)
            return MessageUpdateEvent(
                shard=shard, payload=payload, guild=guild, channel=channel, message=message
            )

        elif event is MessageEvents.DELETE:
            message = await self.delete(payload['id'])
            return MessageDeleteEvent(
                shard=shard, payload=payload, guild=guild, channel=channel, message=message
            )

        elif event is MessageEvents.BULK_DELETE:
            messages: typing.List[Message] = []

            for message_id in payload['ids']:
                message = await self.delete(message_id)

                if message is not None:
                    messages.append(message)

            return MessageBulkDeleteEvent(
                shard=shard, payload=payload, guild=guild, channel=channel, messages=messages
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

    async def create(self, *, content: str) -> None:
        await self.client.rest.request(
            CREATE_CHANNEL_MESSAGE, channel_id=self.channel_id, json={'content': str(content)}
        )
