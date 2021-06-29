from .basestate import BaseState, BaseSubState
from .. import rest
from ..objects.webhookobject import Webhook
from ..utils import Snowflake, _validate_keys


__all__ = ('WebhookState')


class WebhookState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __webhook_class__ = Webhook

    async def fetch(self, webhook_id):
        data = await rest.get_webhook.request(
            fmt={'webhook_id': Snowflake.try_snowflake(webhook_id)}
        )
        return self.upsert(data)

    def upsert(self, data):
        webhook = self.get(data['id'])
        if webhook is not None:
            webhook.update(data)
        else:
            webhook = self.__webhook_class__.unmarshal(data, state=self)
            webhook.cache()

        return webhook


class ChannelWebhookState(BaseSubState):
    def __init__(self, *, superstate, channel) -> None:
        super().__init__(superstate=superstate)
        self.channel = channel

    async def create(self, **kwargs):
        _validate_keys(
            f'{self.__class__.__name__}.create', kwargs, ('name',),
            rest.create_webhook.json)
        data = await rest.create_webhook.request(
            session=self.superstate.client.rest,
            json=kwargs, fmt={'channel_id': self.channel.id}
        )

        return self.superstate.upsert(data)

    async def fetch_many(self):
        data = await rest.get_channel_webhooks.request(
            session=self.superstate.client.rest,
            fmt={'channel_id': self.channel.id}
        )

        self._keys.update(Snowflake(webhook['id']) for webhook in data)

        return self.superstate.upsert_many(data)
