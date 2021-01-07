from datetime import datetime

from .bases import (
    BaseObject,
    BaseState
)

from .utils import (
    JsonStructure,
    JsonField,
    JsonArray,
    Snowflake,
    _try_snowflake
)

from typing import (
    TYPE_CHECKING,
    List,
    Union
)

if TYPE_CHECKING:
    from .channel import (
        _Channel,
        ChannelState,
    )


class MessageType:
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_GUILD_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    REPLY = 19
    APPLICATION_COMMAND = 20


class MessageActivity(JsonStructure):
    __json_fields__ = {
        'type': JsonField('type'),
        'party_id': JsonField('party_id'),
    }

    type: int
    party_id: str


class MessageApplication(BaseObject):
    __json_fields__ = {
        'cover_image': JsonField('cover_image'),
        'description': JsonField('description'),
        'icon': JsonField('icon'),
        'name': JsonField('name'),
    }

    id: Snowflake
    cover_image: str
    description: str
    icon: str
    name: str


class MessageReference(JsonStructure):
    __json_fields__ = {
        'message_id': JsonField('message_id', Snowflake, str),
        'channel_id': JsonField('channel_id', Snowflake, str),
        'guild_id': JsonField('guild_id', int, str),
    }

    message_id: Snowflake
    channel_id: Snowflake
    guild_id: Snowflake


class MessageActivityType:
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5


class MessageFlag:
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPRESS_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4


class MessageSticker(BaseObject):
    __json_fields__ = {
        'pack_id': JsonField('pack_id', Snowflake, str),
        'name': JsonField('name'),
        'description': JsonField('description'),
        'tags': JsonField('tags'),
        'asset': JsonField('asset'),
        'preview_asset': JsonField('preview_asset'),
        'format_type': JsonField('format_type'),
    }

    id: Snowflake
    pack_id: Snowflake
    name: str
    description: str
    tags: str
    asset: str
    preview_asset: str
    format_type: int


class MessageStickerType:
    PNG = 1
    APNG = 2
    LOTTIE = 3


class FollowedChannel(JsonStructure):
    __json_fields__ = {
        'channel_id': JsonField('channel_id', Snowflake, str),
        'webhook_id': JsonField('webhook_id', Snowflake, str),
    }

    channel_id: Snowflake
    webhook_id: Snowflake


class Reaction(JsonStructure):
    __json_fields__ = {
        'count': JsonField('count'),
        'me': JsonField('me'),
        'emoji': JsonField('emoji'),
    }

    count: int
    me: bool
    emoji: ...

    def __init__(self, state, message):
        self._state = state
        self.message = message

    async def remove(self, user=None):
        await self._state.remove(self.emoji, user)

    async def remove_all(self):
        await self._state.remove_emoji(self.emoji)


class EmbedType:
    RICH = 'rich'
    IMAGE = 'image'
    VIDEO = 'video'
    GIFV = 'gifv'
    ARTICLE = 'article'
    LINK = 'link'


class EmbedAttachment(JsonStructure):
    __json_fields__ = {
        'url': JsonField('url'),
        'proxy_url': JsonField('proxy_url'),
        'height': JsonField('height'),
        'width': JsonField('width'),
    }

    url: str
    proxy_url: ...
    height: ...
    width: ...


class EmbedVideo(JsonStructure):
    __json_fields__ = {
        'url': JsonField('url'),
        'height': JsonField('height'),
        'width': JsonField('width'),
    }

    url: str
    height: int
    width: int


class EmbedProvider(JsonStructure):
    __json_fields__ = {
        'name': JsonField('name'),
        'url': JsonField('url'),
    }

    name: str
    url: str


class EmbedAuthor(JsonStructure):
    __json_fields__ = {
        'name': JsonField('name'),
        'url': JsonField('url'),
        'icon_url': JsonField('icon_url'),
        'proxy_icon_url': JsonField('proxy_icon_url'),
    }

    name: str
    url: str
    icon_url: str
    proxy_icon_url: str


class EmbedFooter(JsonStructure):
    __json_fields__ = {
        'text': JsonField('text'),
        'icon_url': JsonField('icon_url'),
        'proxy_icon_url': JsonField('proxy_icon_url'),
    }

    text: str
    icon_url: str
    proxy_icon_url: str


class EmbedField(JsonStructure):
    __json_fields__ = {
        'name': JsonField('name'),
        'value': JsonField('value'),
        'inline': JsonField('inline'),
    }

    name: str
    value: str
    inline: bool


class Embed(JsonStructure):
    __json_fields__ = {
        'title': JsonField('title'),
        'type': JsonField('type'),
        'description': JsonField('description'),
        'url': JsonField('url'),
        'color': JsonField('color'),
        'footer': JsonField('footer', struct=EmbedFooter),
        'image': JsonField('image', struct=EmbedAttachment),
        'thumbnail': JsonField('thumbnail', struct=EmbedAttachment),
        'video': JsonField('video', struct=EmbedVideo),
        'provider': JsonField('provider', struct=EmbedProvider),
        'author': JsonField('author', struct=EmbedAuthor),
        'fields': JsonArray('fields', struct=EmbedField),
    }
    title: str
    type: str
    description: str
    url: str
    # timestamp
    color: int
    footer: EmbedFooter
    image: EmbedAttachment
    thumbnail: EmbedAttachment
    video: EmbedVideo
    provider: EmbedProvider
    author: EmbedAuthor
    fields: list

    def __init__(self, *, title=None, description=None, url=None, color=None):
        self.title = title
        self.description = description
        self.url = url
        self.color = color
        self.fields = []

    def set_footer(self, text=None, icon_url=None, proxy_icon_url=None):
        fields = {
            'text': text,
            'icon_url': icon_url,
            'proxy_icon_url': proxy_icon_url
        }
        self.footer = EmbedFooter.unmarshal(fields)
        return self.footer

    def set_image(self, url=None, proxy_url=None, height=None, width=None):
        fields = {
            'url': url,
            'proxy_url': proxy_url,
            'height': height,
            'width': width
        }
        self.image = EmbedAttachment.unmarshal(fields)
        return self.image

    def set_thumbnail(self, url=None, proxy_url=None, height=None, width=None):
        fields = {
            'url': url,
            'proxy_url': proxy_url,
            'height': height,
            'width': width
        }
        self.thumbnail = EmbedAttachment.unmarshal(fields)
        return self.thumbnail

    def set_video(self, url=None, width=None, height=None):
        fields = {
            'url': url,
            'width': width,
            'height': height
        }
        self.video = EmbedVideo.unmarshal(fields)
        return self.video

    def set_provider(self, name=None, url=None):
        fields = {
            'name': name,
            'url': url
        }
        self.provider = EmbedProvider.unmarshal(fields)
        return self.provider

    def set_author(
        self,
        name=None,
        url=None,
        icon_url=None,
        proxy_icon_url=None
    ):
        fields = {
            'name': name,
            'url': url,
            'icon_url': icon_url,
            'proxy_icon_url': proxy_icon_url
        }
        self.author = EmbedAuthor.unmarshal(fields)
        return self.author

    def add_field(self, name, value, inline=False):
        fields = {
            'name': name,
            'value': value,
            'inline': inline
        }
        field = EmbedField.unmarshal(fields)
        self.fields.append(field)
        return field


class MessageAttachment(BaseObject):
    __json_fields__ = {
        'filename': JsonField('filename'),
        'size': JsonField('size'),
        'url': JsonField('url'),
        'proxy_url': JsonField('proxy_url'),
        'height': JsonField('height'),
        'width': JsonField('width'),
    }

    filename: str
    size: int
    url: str
    proxy_url: str
    height: int
    width: int


class ChannelMention(BaseObject):
    __json_fields__ = {
        'guild_id': JsonField('int', int, str),
        'type': JsonField('int'),
        'name': JsonField('name'),
    }

    guild_id: Snowflake
    type: int
    name: str


class AllowedMentionsType:
    ROLES = 'roles'
    USERS = 'users'
    EVERYONE = 'everyone'


class AllowedMentions(JsonStructure):
    __json_fields__ = {
        'parse': JsonArray('parse'),
        'roles': JsonArray('roles', Snowflake, str),
        'users': JsonArray('users', Snowflake, str),
        'replied_user': JsonField('replied_user'),
    }

    parse: ...
    roles: List[Snowflake]
    users: List[Snowflake]
    replied_user: bool


class Message(BaseObject):
    __slots__ = (
        'id', 'channel_id', 'guild_id', 'channel', 'guild', '_author',
        'author', '_member', 'content', 'tts', 'mention_everyone',
        'attachments', 'embeds', 'reactions', 'nonce', 'pinned', 'webhook_id',
        'type', 'activity', 'appliaction', 'flags', 'stickers'
    )

    __json_fields__ = {
        'channel_id': JsonField('channel_id', Snowflake, str),
        'guild_id': JsonField('guild_id', Snowflake, str),
        '_author': JsonField('author'),
        '_member': JsonField('member'),
        'content': JsonField('content'),
        'tts': JsonField('tts'),
        'mention_everyone': JsonField('mention_everyone'),
        'attachments': JsonArray('attachments', struct=MessageAttachment),
        'embeds': JsonArray('embeds', struct=Embed, init_struct_class=False),
        '_reactions': JsonArray('reactions'),
        'nonce': JsonField('nonce'),
        'pinned': JsonField('pinned'),
        'webhook_id': JsonField('webhook_id', int, str),
        'type': JsonField('type'),
        'activity': JsonField('activity', struct=MessageActivity),
        'application': JsonField('application'),
        'flags': JsonField('flags'),
        'stickers': JsonArray('stickers', struct=MessageSticker),
    }

    id: Snowflake
    channel_id: Snowflake
    guild_id: Snowflake
    _author: dict
    _member: dict
    content: str
    # timestamp
    # edited_timestamp
    tts: bool
    mention_everyone: bool
    # mentions
    # mention_roles
    # mention_channels
    attachments: list
    embeds: list
    _reactions: list
    nonce: Union[str, int]
    pinned: bool
    webhook_id: int
    type: int
    activity: MessageActivity
    application: MessageApplication
    # message_reference
    flags: int
    stickers: list

    # referenced_message

    def __init__(self, *, state: 'ChannelState', channel: '_Channel'):
        self._state = state
        self.channel = channel
        self.reactions = ReactionState(self._state._client, self)

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._reactions is not None:
            for reaction in self._reactions:
                self.reactions._add(reaction)

        if self.channel is not None:
            self.guild = self.channel.guild

        if self.guild is not None and self._member is not None:
            if self._member.get('user') is None:
                self._member['user'] = self._author
            self.author = self.guild.members._add(self._member)
        else:
            self.author = self._state._client.users._add(self._author)

    async def crosspost(self):
        rest = self._state._client.rest
        resp = await rest.crosspost_message(self.channel.id, self.id)
        data = await resp.json()
        message = self._state._add(data, channel=self.channel)
        return message

    async def edit(
        self,
        content=None,
        *,
        embed=None,
        flags=None,
        allowed_mentions=None
    ):
        rest = self._state._client.rest
        resp = await rest.edit_message(
            self.channel.id,
            self.id,
            content=content,
            embed=embed,
            flags=flags,
            allowed_mentions=allowed_mentions
        )
        data = await resp.json()
        message = self._state._add(data, channel=self.channel)
        return message

    async def delete(self):
        rest = self._state._client.rest
        await rest.edit_message(self.channel.id, self.id)

    async def pin(self):
        rest = self._state._client.rest
        await rest.pin_message(self.id)

    async def unpin(self):
        rest = self._state._client.rest
        await rest.unpin_message(self.id)


class ReactionState(BaseState):
    def __init__(self, client, message):
        super().__init__(client)
        self._message = message

    def _add(self, data) -> Reaction:
        reaction = self.get(data['emoji'])
        if reaction is not None:
            reaction._update(data, set_default=False)
            return reaction
        reaction = Reaction.unmarshal(data)
        self._values[reaction.emoji] = reaction
        return reaction

    async def add(self, emoji):
        rest = self._client.rest
        await rest.create_reaction(
            self._message.channel.id,
            self._message.id,
            emoji
        )

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_reactions(
            self._message.channel.id,
            self._message.id
        )
        data = await resp.json()
        reactions = []
        for reaction in data:
            reaction = self._add(reaction)
            reactions.append(reaction)
        return reactions

    async def remove(self, emoji, user=None):
        if user is not None:
            user = user.id

        rest = self._client.rest
        await rest.delete_reaction(
            self._message.channel.id,
            self._message.id,
            emoji,
            user
        )

    async def remove_emoji(self, emoji):
        rest = self._client.rest
        await rest.delete_reactions(
            self._message.channel.id,
            self._message.id,
            emoji
        )

    async def remove_all(self, emoji):
        rest = self._client.rest
        await rest.delete_reactions(self._message.channel.id, self._message.id)


class MessageState(BaseState):
    def __init__(self, client, channel: '_Channel'):
        super().__init__(client)
        self._channel = channel

    def _add(self, data) -> Message:
        message = self.get(data['id'])
        if message is not None:
            message._update(data, set_default=False)
            return message
        message = Message.unmarshal(data, state=self, channel=self._channel)
        self._values[message.id] = message
        return message

    async def fetch(self, message_id) -> Message:
        rest = self._client.rest
        resp = await rest.get_channel_message(self._channel.id, message_id)
        data = await resp.json()
        message = self._add(data)
        return message

    async def fetch_history(
        self,
        around=None,
        before=None,
        after=None,
        limit=None
    ):
        around = _try_snowflake(around)
        before = _try_snowflake(before)
        after = _try_snowflake(after)

        if isinstance(around, Snowflake):
            around = around.datetime

        if isinstance(before, Snowflake):
            before = before.datetime

        if isinstance(after, Snowflake):
            after = after.datetime

        if isinstance(around, datetime):
            around = around.timestamp()

        if isinstance(before, datetime):
            before = before.timestamp()

        if isinstance(after, datetime):
            after = after.timestamp()

        rest = self._client.rest
        resp = await rest.get_channel_messages(
            self._channel.id,
            around=around,
            before=before,
            after=after,
            limit=limit
        )
        data = await resp.json()
        messages = []
        for message in data:
            messages.append(self._add(message))
        return messages

    async def bulk_delete(self, messages):
        messages = {message.id for message in messages}
        rest = self._client.rest
        await rest.bulk_delete_messages(self._channel.id, messages)

    async def fetch_pins(self):
        rest = self._client.rest
        await rest.get_pinned_message(self._channel.id)
