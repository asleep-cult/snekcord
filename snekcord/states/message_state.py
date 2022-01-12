from __future__ import annotations

from typing import Iterable, Optional, TYPE_CHECKING, Union

from .base_state import BaseSate
from ..builders import JSONBuilder
from ..epochs import MessageEpoch
from ..exceptions import UnknownObjectError
from ..mentions import MessageMentions
from ..objects import (
    Message,
    ObjectWrapper,
)
from ..rest.endpoints import (
    CREATE_CHANNEL_MESSAGE,
    DELETE_CHANNEL_MESSAGE,
    DELETE_CHANNEL_MESSAGES,
    GET_CHANNEL_MESSAGE,
    GET_CHANNEL_MESSAGES,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

if TYPE_CHECKING:
    from ..json import JSONData

MessageUnwrappable = Union[Snowflake, Message, str, int, ObjectWrapper]

__all__ = ('MessageState',)


class MessageState(BaseSate):
    def __init__(self, *, client, channel) -> None:
        super().__init__(client=client)
        self.channel = channel

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
            if isinstance(object.state, cls):
                return object.id

            raise TypeError('Expected ObjectWrapper created by MessageState')

        raise TypeError('Expected Snowflake, int, str, Message or ObjectWrapper')

    async def upsert(self, data: JSONData) -> Message:
        """Creates or otherwise updates a message and adds it to the state's cache.

        !!! note
            The member slot will not be propagated if the guild is not cached.
        """
        author = data.get('author')
        if author is not None:
            author = await self.client.users.upsert(author)

        member = data.get('member')
        if member is not None:
            try:
                guild = self.channel.guild.unwrap()
            except UnknownObjectError:
                member = None
            else:
                member = await guild.members.upsert(member)

        message = self.get(data['id'])
        if message is not None:
            message.update(data)
            message.author, message.member = author, member
        else:
            message = Message.unmarshal(data, state=self, author=author, member=member)

        guild_id = data.get('guild_id')
        if guild_id is not None:
            message.guild.set_id(guild_id)

        webhook_id = data.get('webhook_id')
        if webhook_id is not None:
            message.webhook.set_id(webhook_id)

        application_id = data.get('application_id')
        if application_id is not None:
            message.application.set_id(application_id)

        return message

    async def fetch(self, message: MessageUnwrappable) -> Message:
        """Retrieves the message with the corresponding id from Discord."""
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

        if mentions is not undefined:
            if not isinstance(mentions, MessageMentions):
                cls = mentions.__class__
                raise TypeError(
                    f'mentions should be MessageMentions or undefined, got {cls.__name__}'
                )

            body['allowed_mentions'] = mentions.to_dict()

        if reference is not undefined:
            body['message_reference'] = {'message_id': self.unwrap_id(reference)}

        data = await self.client.rest.request(
            CREATE_CHANNEL_MESSAGE, channel_id=self.channel.id, json=body
        )
        assert isinstance(data, dict)

        return await self.upsert(data)

    async def delete(self, message: MessageUnwrappable) -> None:
        message_id = self.unwrap_id(message)
        await self.client.rest.request(DELETE_CHANNEL_MESSAGE, message_id=message_id)

    async def delete_many(self, messages: Iterable[MessageUnwrappable]) -> None:
        message_ids = set()
        for message in messages:
            message_ids.add(self.unwrap_id(message))

        if len(message_ids) <= 1:
            raise TypeError('Cannot bulk delete <= 1 message')

        if len(message_ids) > 100:
            raise TypeError('Cannot bulk delete > 100 messages')

        params = {'message_ids': message_ids}
        await self.client.rest.request(
            DELETE_CHANNEL_MESSAGES, channel_id=self.channel.id, params=params
        )
