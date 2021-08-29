from .basestate import BaseState, BaseSubState
from .. import http
from ..objects.webhookobject import Webhook
from ..resolvers import resolve_data_uri
from ..snowflake import Snowflake


class WebhookState(BaseState):
    def upsert(self, data):
        webhook = self.get(Snowflake(data['id']))

        if webhook is not None:
            webhook.update(data)
        else:
            webhook = Webhook.unmarshal(data, state=self)
            webhook.cache()

        return webhook

    async def fetch(self, webhook, token=None):
        webhook_id = Snowflake.try_snowflake(webhook)

        if token is not None:
            webhook_token = str(token)

            data = await http.get_webhook_with_token.request(
                self.client.http, webhook_id=webhook_id, webhook_token=webhook_token
            )
        else:
            data = await http.get_webhook.request(self.client.http, webbook_id=webhook_id)

        return self.upsert(data)

    async def delete(self, webhook, token=None):
        webhook_id = Snowflake.try_snowflake(webhook)

        if token is not None:
            webhook_token = str(token)

            await http.delete_webhook_with_token.request(
                self.client.http, webhook_id=webhook_id, webhook_token=webhook_token
            )
        else:
            await http.delete_webhook.request(self.client.http, webhook_id=webhook_id)


class ChannelWebhookState(BaseSubState):
    def __init__(self, *, superstate, channel):
        super().__init__(superstate=superstate)
        self.channel = channel

    def upsert(self, data):
        webhook = self.superstate.upsert(data)
        webhook._json_data_['channel_id'] = self.channel._json_data_['id']
        webhook._json_data_['guild_id'] = self.channel._json_data_['guild_id']

        self.add_key(webhook.id)

        return webhook

    async def fetch_all(self):
        data = await http.get_channel_webhooks.request(
            self.superstate.client.http, channel_id=self.channel.id
        )

        return [self.upsert(webhook) for webhook in data]

    async def create(self, *, name, avatar=None):
        json = {'name': str(name)}

        if avatar is not None:
            json['avatar'] = await resolve_data_uri(avatar)

        data = await http.create_webhook.request(
            self.superstate.client.http, channel_id=self.channel.id, json=json
        )

        return self.upsert(data)
