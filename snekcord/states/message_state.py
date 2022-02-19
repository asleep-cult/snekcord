from __future__ import annotations

import typing
from datetime import datetime

from .base_state import (
    CachedEventState,
    CachedStateView,
    OnDecoratorT,
)
from ..builders import (
    MessageCreateBuilder,
    MessageUpdateBuilder,
)
from ..cache import (
    RefStore,
    SnowflakeMemoryRefStore,
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
from ..ordering import FetchOrdering
from ..rest.endpoints import (
    ADD_CHANNEL_PIN,
    CROSSPOST_CHANNEL_MESSAGE,
    DELETE_CHANNEL_MESSAGE,
    DELETE_CHANNEL_MESSAGES,
    GET_CHANNEL_MESSAGE,
    GET_CHANNEL_MESSAGES,
    GET_CHANNEL_PINS,
    REMOVE_CHANNEL_PIN,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

if typing.TYPE_CHECKING:
    from .channel_state import SupportsChannelID
    from ..clients import Client
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
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.channel_refstore = self.create_channel_refstore()

    def create_channel_refstore(self) -> RefStore[Snowflake, Snowflake]:
        return SnowflakeMemoryRefStore()

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

    async def for_channel(self, channel: SupportsChannelID) -> ChannelMessagesView:
        channel_id = self.client.channels.to_unique(channel)

        messages = await self.channel_refstore.get(channel_id)
        return self.client.create_channel_messages_view(messages, channel_id)

    async def upsert(self, data: JSONObject) -> Message:
        message_id = Snowflake.into(data, 'id')
        assert message_id is not None

        guild_id = Snowflake.into(data, 'guild_id')

        channel_id = Snowflake.into(data, 'channel_id')
        if channel_id is not None:
            await self.channel_refstore.add(channel_id, message_id)

            if guild_id is None:
                channel = await self.client.channels.cache.get(channel_id)

                if channel is not None:
                    data['guild_id'] = channel.guild_id

        author = data.get('author')
        if author is not None:
            data['author_id'] = Snowflake(author['id'])
            await self.client.users.upsert(author)

        timestamp = data.get('timestamp')
        if timestamp is None:
            data['timestamp'] = message_id.to_datetime().isoformat()

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
            client=self.client,
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
            await self.channel_refstore.remove(object.channel_id, object.id)

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
            message = await self.drop(payload['id'])
            return MessageDeleteEvent(
                shard=shard, payload=payload, guild=guild, channel=channel, message=message
            )

        elif event is MessageEvents.BULK_DELETE:
            messages: typing.List[Message] = []

            for message_id in payload['ids']:
                message = await self.drop(message_id)

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

    async def crosspost(self, message: SupportsMessageID) -> Message:
        data = await self.client.rest.request_api(
            CROSSPOST_CHANNEL_MESSAGE,
            channel_id=self.channel_id,
            message_id=self.to_unique(message),
        )
        assert isinstance(data, dict)

        return await self.client.messages.upsert(data)

    async def pin(self, message: SupportsMessageID) -> None:
        await self.client.rest.request_api(
            ADD_CHANNEL_PIN, channel_id=self.channel_id, message_id=self.to_unique(message)
        )

    async def unpin(self, message: SupportsMessageID) -> None:
        await self.client.rest.request_api(
            REMOVE_CHANNEL_PIN, channel_id=self.channel_id, message_id=self.to_unique(message)
        )

    async def fetch_pins(self) -> typing.List[Message]:
        data = await self.client.rest.request_api(GET_CHANNEL_PINS, channel_id=self.channel_id)
        assert isinstance(data, list)

        return [await self.client.messages.upsert(message) for message in data]

    def create(
        self,
        *,
        content: MaybeUndefined[str] = undefined,
        tts: MaybeUndefined[bool] = undefined,
        # embeds, allowed mentions, message reference
        # components, stickers, attachments
        flags: MaybeUndefined[MessageFlags] = undefined,
    ) -> MessageCreateBuilder:
        builder = MessageCreateBuilder(client=self.client, channel_id=self.channel_id)

        if content is not undefined:
            builder.content(content)

        if tts is not undefined:
            builder.tts(tts)

        if flags is not undefined:
            builder.flags(flags)

        return builder

    async def fetch(self, message: SupportsMessageID) -> Message:
        data = await self.client.rest.request_api(
            GET_CHANNEL_MESSAGE, channel_id=self.channel_id, message_id=self.to_unique(message)
        )
        assert isinstance(data, dict)

        return await self.client.messages.upsert(data)

    async def fetch_many(
        self,
        ordering: MaybeUndefined[FetchOrdering] = undefined,
        point: MaybeUndefined[typing.Union[SupportsMessageID, datetime]] = undefined,
        *,
        limit: MaybeUndefined[int] = undefined,
    ) -> typing.List[Message]:
        params = {}

        if point is not undefined:
            if isinstance(point, datetime):
                snowflake = Snowflake.build(point)
            else:
                snowflake = self.client.messages.to_unique(point)

            assert ordering is not undefined
            params[ordering.value] = snowflake

        if limit is not undefined:
            params['limit'] = int(limit)

        data = await self.client.rest.request_api(
            GET_CHANNEL_MESSAGES, channel_id=self.channel_id, params=params
        )
        assert isinstance(data, list)

        return [await self.client.messages.upsert(message) for message in data]

    def update(
        self,
        message: SupportsMessageID,
        *,
        content: MaybeUndefined[typing.Optional[str]] = undefined,
        flags: MaybeUndefined[typing.Optional[MessageFlags]] = undefined,
    ) -> MessageUpdateBuilder:
        builder = MessageUpdateBuilder(
            client=self.client, channel_id=self.channel_id, message_id=self.to_unique(message)
        )

        if content is not undefined:
            builder.content(content)

        if flags is not undefined:
            builder.flags(flags)

        return builder

    async def delete(self, message: SupportsMessageID) -> typing.Optional[Message]:
        message_id = self.client.messages.to_unique(message)

        await self.client.rest.request_api(
            DELETE_CHANNEL_MESSAGE, channel_id=self.channel_id, message_id=message_id
        )
        return await self.client.messages.drop(message_id)

    async def delete_many(
        self, messages: typing.Iterable[SupportsMessageID]
    ) -> typing.List[Message]:
        message_ids = {str(self.to_unique(message)) for message in messages}

        if not 1 < len(message_ids) <= 100:
            raise ValueError('len(messages) should be > 1 and <= 100')

        await self.client.rest.request_api(
            DELETE_CHANNEL_MESSAGES,
            channel_id=self.channel_id,
            json={'messages': tuple(message_ids)},
        )

        iterator = (await self.client.messages.drop(message_id) for message_id in message_ids)
        return [message async for message in iterator if message is not None]
