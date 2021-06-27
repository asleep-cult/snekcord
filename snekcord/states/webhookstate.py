from __future__ import annotations

import typing as t

from .basestate import BaseState, BaseSubState
from .. import rest
from ..objects.channelobject import TextChannel
from ..objects.webhookobject import Webhook
from ..utils import Snowflake, _validate_keys

if t.TYPE_CHECKING:
    from ..typing import Json, SnowflakeType


__all__ = ('WebhookState')


class WebhookState(BaseState[Snowflake, Webhook]):
    __key_transformer__ = Snowflake.try_snowflake
    __webhook_class__ = Webhook

    async def fetch(self, webhook_id: SnowflakeType) -> Webhook:
        data = await rest.get_webhook.request(
            fmt={'webhook_id': Snowflake.try_snowflake(webhook_id)}
        )
        return self.upsert(data)

    def upsert(self, data: Json) -> Webhook:  # type: ignore
        webhook = self.get(data['id'])
        if webhook is not None:
            webhook.update(data)
        else:
            webhook = self.__webhook_class__.unmarshal(data, state=self)
            webhook.cache()

        return webhook


class ChannelWebhookState(BaseSubState[Snowflake, Webhook]):
    if t.TYPE_CHECKING:
        channel: TextChannel
        superstate: WebhookState

    def __init__(
        self, *, superstate: WebhookState, channel: TextChannel
    ) -> None:
        super().__init__(superstate=superstate)
        self.channel = channel

    async def create(self, **kwargs: t.Any) -> Webhook:
        _validate_keys(
            f'{self.__class__.__name__}.create', kwargs, ('name',),
            rest.create_webhook.json)
        data = await rest.create_webhook.request(
            session=self.superstate.client.rest,
            json=kwargs, fmt={'channel_id': self.channel.id}
        )

        return self.superstate.upsert(data)

    async def fetch_many(self) -> t.Set[Webhook]:
        data = await rest.get_channel_webhooks.request(
            session=self.superstate.client.rest,
            fmt={'channel_id': self.channel.id}
        )

        self._keys.update(Snowflake(webhook['id']) for webhook in data)

        return self.superstate.upsert_many(data)
