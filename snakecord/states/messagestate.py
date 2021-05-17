from .basestate import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from .. import rest
from ..objects.messageobject import Message
from ..utils import Snowflake, _validate_keys


class MessageState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __message_class__ = Message

    def __init__(self, *, manager, channel):
        super().__init__(manager=manager)
        self.channel = channel

    def append(self, data):
        message = self.get(data['id'])
        if message is not None:
            message.update(data)
        else:
            message = self.__message_class__.unmarshal(data, state=self)
            message.cache()

        return message

    async def bulk_fetch(self, around=None, before=None, after=None,
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
            session=self.manager.rest,
            fmt=dict(channel_id=self.channel.id),
            params=params)

        return self.extend(data)

    async def fetch(self, message):
        message_id = Snowflake.try_snowflake(message)

        data = await rest.get_channel_messages.request(
            session=self.manager.rest,
            fmt=dict(channel_id=self.channel.id, message_id=message_id))

        return self.append(data)

    async def create(self, **kwargs):
        keys = rest.create_channel_message.json

        try:
            kwargs['embed'] = kwargs['embed'].to_dict()
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, (), keys)

        data = await rest.create_channel_message.request(
            session=self.manager.rest,
            fmt=dict(channel_id=self.channel.id),
            json=kwargs)

        return self.append(data)
