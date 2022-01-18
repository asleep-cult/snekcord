from __future__ import annotations

from typing import Iterable, Optional, TYPE_CHECKING, Union

from .base_state import (
    BaseClientState,
    BaseSubsidiaryState,
)
from ..builders import JSONBuilder
from ..collection import Collection
from ..epochs import MessageEpoch
from ..events import (
    BaseEvent,
    MessageBulkDeleteEvent,
    MessageCreateEvent,
    MessageDeleteEvent,
    MessageEvent,
    MessageUpdateEvent,
)
from ..intents import WebSocketIntents
from ..mentions import MessageMentions
from ..objects import (
    BaseChannel,
    Message,
    ObjectWrapper,
)
from ..rest.endpoints import (
    CREATE_CHANNEL_MESSAGE,
    DELETE_CHANNEL_MESSAGES,
    GET_CHANNEL_MESSAGE,
    GET_CHANNEL_MESSAGES,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, UndefinedType, undefined

if TYPE_CHECKING:
    from ..clients import Client
    from ..json import JSONData
    from ..websockets import ShardWebSocket

__all__ = ('MessageUnwrappable', 'MessageState', 'ChannelMessageState')

MessageUnwrappable = Union[Snowflake, Message, str, int, ObjectWrapper]


class MessageState(BaseClientState):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self._direct_messages = False

    @classmethod
    def unwrap_id(cls, object: MessageUnwrappable) -> Snowflake:
        """Converts an object into a message id.

        Raises:
            TypeError: The object is not a Snowflake, integer, string,
                Message or ObjectWrapper created by a message state.
        """
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (int, str)):
            return Snowflake(object)

        if isinstance(object, Message):
            return object.id

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, ChannelMessageState):
                return object.id

            raise TypeError('Expected ObjectWrapper created by ChannelMessageState')

        raise TypeError('Expected Snowflake, int, str, Message or ObjectWrapper')

    def on_create(self):
        return self.on(MessageEvent.CREATE)

    def on_update(self):
        return self.on(MessageEvent.UPDATE)

    def on_delete(self):
        return self.on(MessageEvent.DELETE)

    def on_bulk_delete(self):
        return self.on(MessageEvent.BULK_DELETE)

    def get_events(self) -> type[MessageEvent]:
        return MessageEvent

    def get_intents(self):
        intents = WebSocketIntents.GUILD_MESSAGES

        if self._direct_messages:
            intents |= WebSocketIntents.DIRECT_MESSAGES

        return intents

    def listen(self, *, direct_messages=False):
        self._direct_messages = direct_messages
        return super().listen()

    async def process_event(
        self, event: str, shard: ShardWebSocket, payload: JSONData
    ) -> BaseEvent:
        event = self.cast_event(event)

        if event is MessageEvent.CREATE:
            channel = self.client.channels.get(payload['channel_id'])
            if channel is not None:
                message = await channel.messages.upsert(payload)
            else:
                message = None

            return MessageCreateEvent(shard=shard, payload=payload, message=message)

        if event is MessageEvent.UPDATE:
            channel = self.client.channels.get(payload['channel_id'])
            if channel is not None:
                message = await channel.messages.upsert(payload)
            else:
                message = None

            return MessageUpdateEvent(shard=shard, payload=payload, message=message)

        if event is MessageEvent.DELETE:
            channel = self.client.channels.get(payload['channel_id'])
            if channel is not None:
                message = channel.messages.pop(payload['id'])
            else:
                message = None

            return MessageDeleteEvent(shard=shard, payload=payload, message=message)

        if event is MessageEvent.BULK_DELETE:
            messages = Collection()

            channel = self.client.channels.get(payload['channel_id'])
            if channel is not None:
                for message_id in payload['ids']:
                    message = channel.messages.pop(message_id)

                    if message is not None:
                        messages[message.id] = message

            return MessageBulkDeleteEvent(shard=shard, payload=payload, messages=messages)


class ChannelMessageState(BaseSubsidiaryState):
    def __init__(self, *, superstate: BaseClientState, channel: BaseChannel) -> None:
        super().__init__(superstate=superstate)
        self.channel = channel

    async def upsert(self, data: JSONData) -> Message:
        message = self.get(data['id'])
        if message is not None:
            message.update(data)
        else:
            message = Message.unmarshal(data, state=self)

        author = data.get('author')
        if author is not None:
            await message._update_author(author)

        member = data.get('member')
        if member is not None:
            # await message._update_member(member)
            pass

        guild_id = data.get('guild_id')
        if guild_id is not None:
            message.guild.set_id(guild_id)

        webhook_id = data.get('webhook_id')
        if webhook_id is not None:
            # message.webhook.set_id(webhook_id)
            pass

        application_id = data.get('application_id')
        if application_id is not None:
            # message.application.set_id(application_id)
            pass

        return message

    async def fetch(self, message: MessageUnwrappable) -> Message:
        message_id = self.unwrap_id(message)

        data = await self.client.rest.request(
            GET_CHANNEL_MESSAGE, channel_id=self.channel.id, message_id=message_id
        )
        assert isinstance(data, dict)

        return await self.upsert(data)

    async def fetch_many(self, epoch: Optional[MessageEpoch] = None, *, limit: int = 100):
        params = JSONBuilder()

        if epoch is not None:
            if not isinstance(epoch, MessageEpoch):
                raise TypeError(
                    f'epoch should be a MessageEpoch or None, got {epoch.__class__.__name__}'
                )

            params.snowflake(epoch.key, epoch.snowflake)

        params.int('limit', limit)

        messages = await self.client.rest.request(
            GET_CHANNEL_MESSAGES, channel_id=self.channel.id, params=params
        )
        assert isinstance(messages, list)

        return [await self.upsert(message) for message in messages]

    async def create(
        self,
        *,
        content: MaybeUndefined[str] = undefined,
        tts: MaybeUndefined[bool] = undefined,
        embeds=undefined,
        mentions: MaybeUndefined[MessageMentions] = undefined,
        reference=undefined,
        components=undefined,
        stickers=undefined,
        attachments=undefined,
    ) -> Message:
        body = JSONBuilder()

        body.str('content', content)
        body.bool('tts', tts)

        if not isinstance(mentions, (MessageMentions, UndefinedType)):
            cls = mentions.__class__
            raise TypeError(
                f'mentions should be MessageMentions or undefined, got {cls.__name__!r}'
            )

        body.set('allowed_mentions', mentions, transformer=MessageMentions.to_dict)

        if reference is not undefined:
            body['message_reference'] = {'message_id': self.unwrap_id(reference)}

        data = await self.client.rest.request(
            CREATE_CHANNEL_MESSAGE, channel_id=self.channel.id, json=body
        )
        assert isinstance(data, dict)

        return await self.upsert(data)

    async def delete_many(self, messages: Iterable[MessageUnwrappable]) -> None:
        message_ids = {self.unwrap_id(message) for message in messages}

        if len(message_ids) <= 1:
            raise TypeError('Cannot bulk delete <= 1 message')

        if len(message_ids) > 100:
            raise TypeError('Cannot bulk delete > 100 messages')

        params = {'message_ids': message_ids}
        await self.client.rest.request(
            DELETE_CHANNEL_MESSAGES, channel_id=self.channel.id, params=params
        )
