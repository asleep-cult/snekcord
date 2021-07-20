import copy
from datetime import datetime

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .embedobject import Embed
from .. import rest
from ..clients.client import ClientClasses
from ..enums import MessageType
from ..flags import MessageFlags
from ..states.messagestate import _embed_to_dict
from ..utils import JsonArray, JsonField, JsonObject, Snowflake, undefined

__all__ = ('MessageMentions', 'MessageReference', 'Message')


class MessageMentions:
    def __init__(self, *, message, everyone, users, roles, channels):
        self.message = message

        self.everyone = everyone

        self.raw_users = copy.deepcopy(users)
        self.raw_roles = copy.deepcopy(roles)
        self.raw_channels = copy.deepcopy(channels)

        self.user_ids = tuple(Snowflake(user['id']) for user in users)
        self.role_ids = tuple(Snowflake(role_id) for role_id in roles)
        self.channel_ids = tuple(Snowflake(channel['id']) for channel in channels)

        for user in users:
            if 'member' in user:
                if message.guild is not None:
                    member = user['member']
                    member['user'] = user
                    message.guild.members.upsert(member)
            else:
                message.state.client.users.upsert(user)

        for channel in channels:
            message.state.client.channels.upsert(channel)

    def get_members(self):
        if self.message.guild is not None:
            for user_id in self.user_ids:
                try:
                    yield self.message.guild.members[user_id]
                except KeyError:
                    continue

    def get_users(self):
        for user_id in self.user_ids:
            try:
                yield self.message.state.client.users[user_id]
            except KeyError:
                continue

    def get_roles(self):
        if self.message.guild is not None:
            for role_id in self.role_ids:
                try:
                    yield self.message.guild.roles[role_id]
                except KeyError:
                    continue

    def get_channels(self):
        for channel_id in self.channel_ids:
            try:
                yield self.message.state.client.channels[channel_id]
            except KeyError:
                continue


class MessageReference(JsonObject):
    __slots__ = ('source_message',)

    message_id = JsonField('message_id', Snowflake)
    channel_id = JsonField('channel_id', Snowflake)
    guild_id = JsonField('guild_id', Snowflake)

    def __init__(self, *, message):
        self.source_message = message

    @property
    def guild(self):
        return self.source_message.state.client.guilds.get(self.guild_id)

    @property
    def channel(self):
        return self.source_message.state.client.channels.get(self.channel_id)

    @property
    def message(self):
        channel = self.channel
        if channel is not None:
            return channel.messages.get(self.message_id)
        return None


class Message(BaseObject):
    __slots__ = ('author', 'member', 'reference', 'reactions', 'mentions')

    channel_id = JsonField('channel_id', Snowflake)
    guild_id = JsonField('guild_id', Snowflake)
    content = JsonField('content')
    created_at = JsonField('timestamp', datetime.fromisoformat)
    edited_at = JsonField('edited_timestamp', datetime.fromisoformat)
    tts = JsonField('tts')
    _attachments = JsonArray('attachments')
    embeds = JsonArray('embeds', object=Embed)
    nonce = JsonField('nonce')
    pinned = JsonField('pinned')
    webhook_id = JsonField('webhook_id', Snowflake)
    type = JsonField('type', MessageType.get_enum)
    _activity = JsonField('activity')
    _application = JsonField('application')
    application_id = JsonField('application_id', Snowflake)
    flags = JsonField('flags', MessageFlags.from_value)
    _interaction = JsonField('interaction')
    _thread = JsonField('thread')
    _components = JsonArray('components')
    _stickers = JsonField('sticker_items')

    def __init__(self, *, state):
        super().__init__(state=state)

        self.author = None
        self.member = None
        self.reference = None
        self.mentions = None

        self.reactions = ClientClasses.ReactionsState(client=self.state.client, message=self)

    @property
    def channel(self):
        return self.state.channel

    @property
    def guild(self):
        if isinstance(self.channel, GuildChannel):
            return self.channel.guild
        return None

    async def crosspost(self):
        data = await rest.crosspost_message.request(
            self.state.client.rest,
            {'channel_id': self.channel.id, 'message_id': self.id}
        )

        return self.state.upsert(data)

    async def modify(
        self, *, content=undefined, embed=undefined, embeds=undefined, suppress_embeds=undefined,
        # file=undefined, allowed_mentions, attachments, components,
    ):
        json = {'embeds': []}

        if content is not undefined:
            if content is not None:
                json['content'] = str(content)
            else:
                json['content'] = None

        if embed is not undefined:
            if embed is not None:
                json['embeds'].append(_embed_to_dict(embed))
            else:
                json['embeds'] = None

        if embeds is not undefined:
            if embeds is not None:
                json['embeds'].extend([_embed_to_dict(embed) for embed in embeds])
            else:
                json['embeds'] = None

        if suppress_embeds is not undefined:
            json['flags'] = MessageFlags(suppress_embeds=suppress_embeds)

        data = await rest.modify_message.request(
            self.state.client.rest,
            {'channel_id': self.channel.id, 'message_id': self.id},
            json=json
        )

        return self.state.upsert(data)

    def pin(self):
        return self.channel.pins.add(self.id)

    def unpin(self):
        return self.channel.pins.remove(self.id)

    def delete(self):
        return self.state.delete(self.id)

    def _delete(self):
        super()._delete()

        if self.pinned:
            self.channel.pins.remove_key(self.id)

    def update(self, data):
        super().update(data)

        self.mentions = MessageMentions(
            message=self, everyone=data['mention_everyone'], users=data.get('mentions', ()),
            roles=data.get('mention_roles', ()), channels=data.get('mention_channels', ())
        )

        if 'author' in data:
            self.author = self.state.client.users.upsert(data['author'])

            guild = self.guild
            member = data.get('member')

            if member is not None and guild is not None:
                member['user'] = data['author']
                self.member = guild.members.upsert(member)

        if 'reactions' in data:
            reactions = set()

            for reaction in reactions:
                reactions.add(self.reactions.upsert(reaction))

            for emoji_id in set(self.reactions.keys()) - reactions:
                del self.reactions.mapping[emoji_id]

        if 'message_reference' in data:
            self.reference = MessageReference.unmarshal(data['message_reference'], message=self)

            if 'referenced_message' in data:
                referenced_message = data['referenced_message']

                if referenced_message is not None:
                    self.state.upsert(data['referenced_message'])

        if self.pinned:
            self.channel.pins.add_key(self.id)
        else:
            self.channel.pins.remove_key(self.id)

        if self.type == MessageType.CHANNEL_PINNED_MESSAGE:
            self.channel.pins.add_key(self.reference.message_id)

            if self.reference.message is not None:
                self.reference.message._json_data_['pinned'] = True

        return self
