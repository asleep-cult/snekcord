from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..utils import _validate_keys
from ..utils.snowflake import Snowflake

__all__ = ('MessageState',)


class MessageState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake

    def __init__(self, *, client, channel):
        super().__init__(client=client)
        self.channel = channel

    def upsert(self, data):
        message = self.get(data['id'])
        if message is not None:
            message.update(data)
        else:
            message = ClientClasses.Message.unmarshal(data, state=self)
            message.cache()

        return message

    async def fetch(self, message):
        message_id = Snowflake.try_snowflake(message)

        data = await rest.get_channel_message.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.channel.id, message_id=message_id))

        return self.upsert(data)

    async def fetch_many(self, around=None, before=None, after=None,
                         limit=None):
        params = {}

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

    async def create(self, **kwargs):
        try:
            kwargs['embed'] = kwargs['embed'].to_dict()
        except KeyError:
            pass

        try:
            kwargs['embeds'] = [embed.to_dict() for embed in kwargs['embeds']]
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, (), rest.create_channel_message.json)

        data = await rest.create_channel_message.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.channel.id),
            json=kwargs)

        return self.upsert(data)

    async def bulk_delete(self, messages):
        message_ids = tuple(Snowflake.try_snowflake_set(messages))

        await rest.bulk_delete_messages.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.channel.id),
            json=dict(messages=message_ids))
