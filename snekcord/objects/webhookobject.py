from __future__ import annotations

import typing as t

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import _validate_keys, Enum, JsonField, JsonTemplate, Snowflake

__all__ = ('WebhookType', 'Webhook')

if t.TYPE_CHECKING:
    from .channelobject import TextChannel
    from .guildobject import Guild
    from .messageobject import Message
    from .userobject import User
    from ..states import BaseState
    from ..typing import Json, SnowflakeType

    WH = t.TypeVar('WH', bound='Webhook')


class WebhookType(Enum[int]):
    incoming = 1
    channel_follower = 2
    application = 3


WebhookTemplate = JsonTemplate(
    type=JsonField('type', WebhookType.get_enum, WebhookType.get_value),
    guild_id=JsonField('guild_id', Snowflake, str),
    channel_id=JsonField('channel_id', Snowflake, str),
    user=JsonField('user'),
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
    if t.TYPE_CHECKING:
        id: Snowflake
        type: WebhookType
        guild_id: t.Optional[Snowflake]
        channel_id: t.Optional[Snowflake]
        user: t.Optional[User]
        name: t.Optional[str]
        avatar: t.Optional[str]
        token: t.Optional[str]
        application_id: t.Optional[Snowflake]
        url: t.Optional[str]
        state: BaseState[Snowflake, Webhook]
        _source_guild: Json
        _source_channel: Json

    @property
    def guild(self) -> t.Optional[Guild]:
        if self.guild_id is not None:
            return self.state.client.guilds.get(self.guild_id)
        return getattr(self.channel, 'guild', None)

    @property
    def channel(self) -> TextChannel:
        if self.channel_id is not None:
            return self.state.client.channels.get(self.channel_id)
        return None

    async def modify(self: WH, **kwargs: t.Any) -> WH:

        _validate_keys(
            f'{self.__class__.__name__}.modify',
            kwargs, (), rest.modify_webhook.json, fmt={'webhook_id': self.id}
        )

        data: Json = await rest.modify_webhook.request(
            session=self.state.client.rest, json=kwargs
        )

        self.update(data)
        return self

    async def delete(self) -> None:
        await rest.delete_webhook.request(
            session=self.state.client.rest, fmt={'webhook_id': self.id}
        )
        self._delete()

    @t.overload
    async def execute(self, *, wait: False, **kwargs: t.Any) -> None:
        ...

    @t.overload
    async def execute(self, *, wait: True, **kwargs: t.Any) -> Message:
        ...

    async def execute(
        self, *, wait: bool = True,
        thread_id: t.Optional[Snowflake] = None,
        **kwargs: t.Any
    ) -> t.Optional[Message]:
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

    async def fetch_message(
        self, message_id: SnowflakeType
    ) -> t.Optional[Message]:
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

    async def edit_message(
        self, message_id: SnowflakeType, **kwargs: t.Any
    ) -> t.Optional[Message]:
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

        data: Json = await rest.edit_webhook_message.request(
            session=self.state.client.rest, json=kwargs,
            fmt={
                'webhook_id': self.id, 'webhook_token': self.token,
                'message_id': Snowflake.try_snowflake(message_id)
            }
        )

        channel = self.channel

        if channel is not None:
            return channel.messages.upsert(data)

    async def delete_message(self, message_id: SnowflakeType) -> None:
        await rest.delete_webhook_message.request(
            fmt={
                'webhook_id': self.id, 'webhook_token': self.token,
                'message_id': Snowflake.try_snowflake(message_id)
            }
        )
