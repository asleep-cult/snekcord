from .baseobject import BaseObject
from .. import rest
from ..clients.client import ClientClasses
from ..enums import WebhookType
from ..fetchables import Fetchable
from ..json import JsonField
from ..resolvers import resolve_data_uri, resolve_embed_data
from ..snowflake import Snowflake
from ..undefined import undefined


class Webhook(BaseObject):
    __slots__ = ('creator', 'source_guild', 'source_channel')

    type = JsonField('type', WebhookType.get_enum)
    guild_id = JsonField('guild_id', Snowflake)
    channel_id = JsonField('channel_id', Snowflake)
    name = JsonField('name')
    token = JsonField('token')
    application_id = JsonField('application_id', Snowflake)
    url = JsonField('url')

    def __init__(self, *, state):
        super().__init__(state=state)

        self.creator = None
        self.source_guild = None
        self.source_channel = None

        self.messages = ClientClasses.WebhookMessageState(client=self.state.client, webhook=self)

    @property
    def guild(self):
        return self.state.client.guils.get(self.guild_id)

    @property
    def channel(self):
        return self.state.client.channels.get(self.channel_id)

    async def execute(
        self, *, content=None, username=None, avatar=None, tts=None, embed=None, embeds=None,
        mentions=None, wait=None, thread=None  # file, components
    ):
        json = {}

        if content is not None:
            json['content'] = str(content)

        if username is not None:
            json['username'] = str(username)

        if avatar is not None:
            if isinstance(avatar, Fetchable):
                json['avatar_url'] = avatar.url()
            else:
                json['avatar_url'] = str(avatar)

        if tts is not None:
            json['tts'] = bool(tts)

        if embed is not None:
            json['embeds'] = [resolve_embed_data(embed)]

        if embeds is not None:
            if 'embeds' not in json:
                json['embeds'] = []

            json['embeds'].extend(resolve_embed_data(embed) for embed in embeds)

        if mentions is not None:
            json['allowed_mentions'] = mentions.to_dict()

        params = {}

        if wait is not None:
            params['wait'] = bool(wait)

        if thread is not None:
            params['thread_id'] = Snowflake.try_snowflake(thread)

        if not any((json.get('content'), json.get('file'), json.get('embeds'))):
            raise TypeError('None of (content, file, embed(s)) were provided')

        data = await rest.execute_webhook.request(
            self.state.client.rest, webhook_id=self.id, webhook_token=self.token,
            params=params, json=json
        )

        if data:
            return self.messages.upsert(data)

        return None

    async def modify(self, *, name=None, avatar=undefined, channel=None):
        json = {}

        if name is not None:
            json['name'] = str(name)

        if avatar is not None:
            if avatar is not None:
                json['avatar'] = resolve_data_uri(avatar)
            else:
                json['avatar'] = None

        if channel is not None:
            json['channel_id'] = Snowflake.try_snowflake(channel)

        data = await rest.modify_webhook.request(
            self.state.client.rest, webhook_id=self.id, json=json
        )

        return self.state.upsert(data)

    def delete(self):
        return self.state.delete(self.id, getattr(self, 'token', None))

    def _delete(self):
        super()._delete()

        if self.channel is not None:
            self.channel.webhooks.remove_key(self.id)

    def update(self, data):
        super().update(data)

        if self.channel is not None:
            self.channel.webhooks.add_key(self.id)

        if 'user' in data:
            self.creator = self.state.client.users.upsert(data['user'])

        if 'source_guild' in data:
            self.source_guild = self.state.client.guilds.upsert(data['source_guild'])

        if 'source_channel' in data:
            self.source_channel = self.source_guild.channels.upsert(data['source_channel'])

        return self
