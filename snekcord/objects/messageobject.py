import copy
from datetime import datetime

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .embedobject import Embed
from .. import rest
from ..clients.client import ClientClasses
from ..enums import MessageType
from ..flags import MessageFlags
from ..resolvers import resolve_embed_data
from ..utils import JsonArray, JsonField, JsonObject, Snowflake, undefined

__all__ = ('AllowedMentions', 'MessageReference', 'Message')


class AllowedMentions:
    def __init__(self, *, roles=None, users=None, replied_user=None):
        self.parse = []

        if roles is not None:
            if isinstance(roles, bool):
                self.roles = roles
                self.parse.append('roles')
            else:
                self.roles = Snowflake.try_snowflake_many(roles)
        else:
            self.roles = None

        if users is not None:
            if isinstance(users, bool):
                self.users = users
                self.parse.append('users')
            else:
                self.users = Snowflake.try_snowflake_many(users)
        else:
            self.users = None

        if replied_user is not None:
            self.replied_user = bool(replied_user)
        else:
            self.replied_user = None

    def to_dict(self):
        data = {}

        if self.parse:
            data['parse'] = self.parse

        if self.roles is not None:
            data['roles'] = self.roles

        if self.users is not None:
            data['users'] = self.users

        if self.replied_user is not None:
            data['replied_user'] = self.replied_user

        return data


class MessageReference:
    def __init__(self, message, *, ensure_exists=None):
        self.message = message

        if ensure_exists is not None:
            self.ensure_exists = bool(ensure_exists)
        else:
            self.ensure_exists = None

    def to_dict(self):
        data = {
            'message_id': self.message.id
        }

        if self.message.guild is not None:
            data['guild_id'] = self.message.guild.id

        if self.ensure_exists is not None:
            data['fail_if_not_exists'] = self.ensure_exists

        return data


class MessageMentionsData:
    def __init__(self, message, everyone, users, roles, channels):
        self.message = message

        self.everyone = everyone

        self.raw_users = copy.deepcopy(users)
        self.raw_roles = copy.deepcopy(roles)
        self.raw_channels = copy.deepcopy(channels)

        self.user_ids = tuple(Snowflake(user['id']) for user in users)
        self.role_ids = tuple(Snowflake(role_id) for role_id in roles)
        self.channel_ids = tuple(Snowflake(channel['id']) for channel in channels)

        for user in users:
            if message.guild is not None:
                try:
                    member = user.pop('member')
                except KeyError:
                    pass
                else:
                    member['user'] = user
                    message.guild.members.upsert(member)
                    continue

            message.state.client.users.upsert(user)

    def get_members(self):
        if self.message.guild is not None:
            yield from self.message.guild.members.get_all(self.user_ids)

    def get_users(self):
        yield from self.message.state.client.users.get_all(self.user_ids)

    def get_roles(self):
        if self.message.guild is not None:
            yield from self.message.guild.roles.get_all(self.role_ids)

    def get_channels(self):
        yield from self.message.state.client.channels.get_all(self.channel_ids)


class MessageReferenceData(JsonObject):
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
        if self.channel is not None:
            return self.channel.messages.get(self.message_id)
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
        allowed_mentions=undefined,  # file=undefined, allowed_mentions, attachments, components,
    ):
        json = {'embeds': []}

        if content is not undefined:
            if content is not None:
                json['content'] = str(content)
            else:
                json['content'] = None

        if embed is not undefined:
            if embed is not None:
                json['embeds'].append(resolve_embed_data(embed))
            else:
                json['embeds'] = None

        if embeds is not undefined:
            if embeds is not None:
                json['embeds'].extend(resolve_embed_data(embed) for embed in embeds)
            else:
                json['embeds'] = None

        if suppress_embeds is not undefined:
            json['flags'] = MessageFlags(suppress_embeds=suppress_embeds)

        if allowed_mentions is not undefined:
            if allowed_mentions is not None:
                json['mentions'] = allowed_mentions.to_dict()
            else:
                json['mentions'] = None

        data = await rest.modify_message.request(
            self.state.client.rest,
            {'channel_id': self.channel.id, 'message_id': self.id},
            json=json
        )

        return self.state.upsert(data)

    def reply(self, *, ensure_exists=None, mention=None, **kwargs):
        kwargs['message_reference'] = MessageReference(self, ensure_exists=ensure_exists)

        if mention is not None:
            kwargs['allowed_mentions'] = AllowedMentions(replied_user=mention)

        return self.state.create(**kwargs)

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

        self.mentions = MessageMentionsData(
            self, data.get('mention_everyone'), data.get('mentions', ()),
            data.get('mention_roles', ()), data.get('mention_channels', ())
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
            self.reference = MessageReferenceData.unmarshal(data['message_reference'], message=self)

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
