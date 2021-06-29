from __future__ import annotations

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import _validate_keys, Enum, JsonField, JsonTemplate, Snowflake

__all__ = ('WebhookType', 'Webhook')


class WebhookType(Enum[int]):
    incoming = 1
    channel_follower = 2
    application = 3


WebhookTemplate = JsonTemplate(
    type=JsonField('type', WebhookType.get_enum, WebhookType.get_value),
    guild_id=JsonField('guild_id', Snowflake, str),
    channel_id=JsonField('channel_id', Snowflake, str),
    _user=JsonField('user'),
    name=JsonField('name'),
    avatar=JsonField('avatar'),
    application_id=JsonField('application_id', Snowflake, str),
    token=JsonField('token'),
    _source_guild=JsonField('source_guild'),
    _source_channel=JsonField('source_channel'),
    url=JsonField('url'),
    __extends__=(BaseTemplate,)
)


class Webhook(BaseObject, template=WebhookTemplate):
    @property
    def guild(self):
        if self.guild_id is not None:
            return self.state.client.guilds.get(self.guild_id)
        return getattr(self.channel, 'guild', None)

    @property
    def channel(self):
        if self.channel_id is not None:
            return self.state.client.channels.get(self.channel_id)
        return None

    async def modify(self, **kwargs):
        _validate_keys(
            f'{self.__class__.__name__}.modify',
            kwargs, (), rest.modify_webhook.json, fmt={'webhook_id': self.id}
        )

        data = await rest.modify_webhook.request(
            session=self.state.client.rest, json=kwargs
        )

        self.update(data)
        return self

    async def delete(self):
        await rest.delete_webhook.request(
            session=self.state.client.rest, fmt={'webhook_id': self.id}
        )
        self._delete()

    async def execute(self, *, wait=True, thread_id=None, **kwargs):
        if self.token is None:
            raise RuntimeError('Webhook.token cannot be None')

        params = {'wait': wait}

        if thread_id is not None:
            params['thread_id'] = Snowflake.try_snowflake(thread_id)

        try:
            kwargs['embeds'] = [embed.to_dict() for embed in kwargs['embeds']]
        except KeyError:
            pass

        _validate_keys(
            f'{self.__class__.__name__}.execute',
            kwargs, (), rest.execute_webhook.json
        )

        ret = await rest.execute_webhook.request(
            session=self.state.client.rest,
            json=kwargs, params=params,
            fmt={'webhook_id': self.id, 'webhook_token': self.token}
        )

        if wait:
            return ret

        return None

    async def fetch_message(self, message_id):
        if self.token is None:
            raise RuntimeError('Webhook.token cannot be None')
        data = await rest.get_webhook_message.request(
            session=self.state.client.rest, fmt={
                'webhook_id': self.id, 'webhook_token': self.token,
                'message_id': Snowflake.try_snowflake(message_id)
            }
        )

        channel = self.channel

        if channel is not None:
            return channel.messages.upsert(data)

    async def edit_message(self, message_id, **kwargs):
        if self.token is None:
            raise RuntimeError('Webhook.token cannot be None')

        try:
            kwargs['embeds'] = [embed.to_dict() for embed in kwargs['embeds']]
        except KeyError:
            pass

        _validate_keys(
            f'{self.__class__.__name__}.edit_message',
            kwargs, (), rest.edit_webhook_message.json
        )

        data = await rest.edit_webhook_message.request(
            session=self.state.client.rest, json=kwargs,
            fmt={
                'webhook_id': self.id, 'webhook_token': self.token,
                'message_id': Snowflake.try_snowflake(message_id)
            }
        )

        channel = self.channel

        if channel is not None:
            return channel.messages.upsert(data)

    async def delete_message(self, message_id):
        await rest.delete_webhook_message.request(
            fmt={
                'webhook_id': self.id, 'webhook_token': self.token,
                'message_id': Snowflake.try_snowflake(message_id)
            }
        )
