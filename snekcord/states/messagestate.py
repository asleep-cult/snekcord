from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.messageobject import Message
from ..utils import Snowflake, _validate_keys

__all__ = ('MessageState',)

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import DMChannel, GuildChannel
    from ..typing import Json, SnowflakeType

    Channel = t.Union[DMChannel, GuildChannel]


class MessageState(BaseState[Snowflake, Message]):
    __key_transformer__ = Snowflake.try_snowflake
    __message_class__ = Message

    def __init__(
        self, *, client: Client, channel: Channel
    ) -> None:
        super().__init__(client=client)
        self.channel = channel

    def upsert(self, data: Json) -> Message:  # type: ignore
        message = self.get(data['id'])
        if message is not None:
            message.update(data)
        else:
            message = self.__message_class__.unmarshal(data, state=self)
            message.cache()

        return message

    async def fetch(self, message: SnowflakeType):  # type: ignore
        message_id = Snowflake.try_snowflake(message)

        data = await rest.get_channel_message.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.channel.id, message_id=message_id))

        return self.upsert(data)

    async def fetch_many(
        self, around: t.Optional[SnowflakeType] = None,
        before: t.Optional[SnowflakeType] = None,
        after: t.Optional[SnowflakeType] = None,
        limit: t.Optional[SnowflakeType] = None
    ) -> t.Set[Message]:
        params: Json = {}

        if around is not None:
            params['around'] = around

        if before is not None:
            params['before'] = before

        if after is not None:
            params['after'] = after

        if limit is not None:
            params['limit'] = limit

        data = await rest.get_channel_messages.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.channel.id),
            params=params)

        return self.upsert_many(data)

    async def create(self, **kwargs: t.Any) -> Message:
        try:
            kwargs['embed'] = kwargs['embed'].to_dict()
        except KeyError:
            pass

        try:
            kwargs['embeds'] = [embed.to_dict() for embed in kwargs['embeds']]
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.create',  # type: ignore
                       kwargs, (), rest.create_channel_message.json)

        data = await rest.create_channel_message.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.channel.id),
            json=kwargs)

        return self.upsert(data)

    async def bulk_delete(
        self, messages: t.Iterable[SnowflakeType]
    ) -> None:
        message_ids = tuple(Snowflake.try_snowflake_set(messages))

        await rest.bulk_delete_messages.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.channel.id),
            json=dict(messages=message_ids))
