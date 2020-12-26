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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .channel import (
        _Channel,
        ChannelState
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
    type: int = JsonField('type')
    party_id: str = JsonField('party_id')


class MessageApplication(BaseObject):
    cover_image: str = JsonField('cover_image')
    description: str = JsonField('description')
    icon: str = JsonField('icon')
    name: str = JsonField('name')


class MessageReference(JsonStructure):
    message_id = JsonField('message_id', int, str)
    channel_id = JsonField('channel_id', int, str)
    guild_id = JsonField('guild_id', int, str)


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
    pack_id: int = JsonField('pack_id', int, str)
    name: str = JsonField('name')
    description: str = JsonField('description')
    tags: str = JsonField('tags')
    asset: str = JsonField('asset')
    preview_asset: str = JsonField('preview_asset')
    format_type: int = JsonField('format_type')


class MessageStickerType:
    PNG = 1
    APNG = 2
    LOTTIE = 3


class FollowedChannel(JsonStructure):
    channel_id: int = JsonField('channel_id', int, str)
    webhook_id: int = JsonField('webhook_id', int, str)


class Reaction(JsonStructure):
    count: int = JsonField('count')
    me: bool = JsonField('me')
    emoji = JsonField('emoji')

    def __init__(self, state, message):
        self._state = state
        self.message = message

    async def remove(self, user=None):
        await self._state.remove(self.emoji, user)

    async def remove_all(self):
        await self._state.remove_emoji(self.emoji)


class PermissionOverwrite(BaseObject):
    type: int = JsonField('type')
    allow: int = JsonField('allow', int, str)
    deny: int = JsonField('deny', int, set)


class EmbedType:
    RICH = 'rich'
    IMAGE = 'image'
    VIDEO = 'video'
    GIFV = 'gifv'
    ARTICLE = 'article'
    LINK = 'link'


class EmbedAttachment(JsonStructure):
    url: str = JsonField('url')
    proxy_url = JsonField('proxy_url')
    height = JsonField('height')
    width = JsonField('width')


class EmbedVideo(JsonStructure):
    url: str = JsonField('url')
    height: int = JsonField('height')
    width: int = JsonField('width')


class EmbedProvider(JsonStructure):
    name: str = JsonField('name')
    url: str = JsonField('url')


class EmbedAuthor(JsonStructure):
    name: str = JsonField('name')
    url: str = JsonField('url')
    icon_url: str = JsonField('icon_url')
    proxy_icon_url: str = JsonField('proxy_icon_url')


class EmbedFooter(JsonStructure):
    text: str = JsonField('text')
    icon_url: str = JsonField('icon_url')
    proxy_icon_url: str = JsonField('proxy_icon_url')


class EmbedField(JsonStructure):
    name: str = JsonField('name')
    value: str = JsonField('value')
    inline: bool = JsonField('inline')


class Embed(JsonStructure):
    title: str = JsonField('title')
    type: str = JsonField('type')
    description: str = JsonField('description')
    url: str = JsonField('url')
    # timestamp
    color: int = JsonField('color')
    footer: EmbedFooter = JsonField('footer', struct=EmbedFooter)
    image: EmbedAttachment = JsonField('image', struct=EmbedAttachment)
    thumbnail: EmbedAttachment = JsonField('thumbnail', struct=EmbedAttachment)
    video: EmbedVideo = JsonField('video', struct=EmbedVideo)
    provider: EmbedProvider = JsonField('provider', struct=EmbedProvider)
    author: EmbedAuthor = JsonField('author', struct=EmbedAuthor)
    fields: list = JsonArray('fields', struct=EmbedField)

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

    def set_author(self, name=None, url=None, icon_url=None, proxy_icon_url=None):
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
    filename: str = JsonField('filename')
    size: int = JsonField('size')
    url: str = JsonField('url')
    proxy_url: str = JsonField('proxy_url')
    height: int = JsonField('height')
    width: int = JsonField('width')


class ChannelMention(BaseObject):
    guild_id: int = JsonField('int', int, str)
    type: int = JsonField('int')
    name: str = JsonField('name')


class AllowedMentionsType:
    ROLES = 'roles'
    USERS = 'users'
    EVERYONE = 'everyone'


class AllowedMentions(JsonStructure):
    parse: list = JsonArray('parse')
    roles: list = JsonArray('roles', int, str)
    users: list = JsonArray('users', int, str)
    replied_user: bool = JsonField('replied_user')


class Message(BaseObject):
    __json_slots__ = (
        'id', 'channel_id', 'guild_id', 'channel', 'guild', '_author', 'author', '_member', 
        'content', 'tts', 'mention_everyone', 'attachments', 'embeds', 'reactions', 'nonce', 
        'pinned', 'webhook_id', 'type', 'activity', 'appliaction', 'flags', 'stickers'
    )

    channel_id: Snowflake = JsonField('channel_id', Snowflake, str)
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    _author = JsonField('author')
    _member = JsonField('member')
    content: str = JsonField('content')
    # timestamp
    # edited_timestamp
    tts: bool = JsonField('tts')
    mention_everyone: bool = JsonField('mention_everyone')
    # mentions
    # mention_roles
    # mention_channels
    attachments: list = JsonArray('attachments', struct=MessageAttachment)
    embeds: list = JsonArray('embeds', struct=Embed, init_struct_class=False)
    _reactions: list = JsonArray('reactions')
    nonce = JsonField('nonce')
    pinned: bool = JsonField('pinned')
    webhook_id: int = JsonField('webhook_id', int, str)
    type: int = JsonField('type')
    activity: MessageActivity = JsonField('activity', struct=MessageActivity)
    application: MessageApplication = JsonField('application')
    # message_reference
    flags: int = JsonField('flags')
    stickers: list = JsonArray('stickers', struct=MessageSticker)

    # referenced_message

    def __init__(self, *, state: 'ChannelState', channel: '_Channel'):
        self._state = state

        self.reactions = ReactionState(self._state._client, self)
        self.channel = channel

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
            self.author = state._client.users._add(self._author)

        del self._author
        del self._member
        del self._reactions

    async def crosspost(self):
        rest = self._state._client.rest
        resp = await rest.crosspost_message(self.channel.id, self.id)
        data = await resp.json()
        message = self._state._add(data, channel=self.channel)
        return message

    async def edit(self, content=None, *, embed=None, flags=None, allowed_mentions=None):
        rest = self._state._client.rest
        resp = await rest.edit_message(self.channel.id, self.id, content=content, embed=embed, flags=flags, allowed_mentions=allowed_mentions)
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
            reaction._update(data)
            return reaction
        reaction = Reaction.unmarshal(data)
        self._values[reaction.emoji] = reaction
        return reaction

    async def add(self, emoji):
        rest = self._client.rest
        await rest.create_reaction(self._message.channel.id, self._message.id, emoji)

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_reactions(self._message.channel.id, self._message.id)
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
        await rest.delete_reaction(self._message.channel.id, self._message.id, emoji, user)

    async def remove_emoji(self, emoji):
        rest = self._client.rest
        await rest.delete_reactions(self._message.channel.id, self._message.id, emoji)

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
            message._update(data)
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

    async def fetch_history(self, around=None, before=None, after=None, limit=None):
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
        resp = await rest.get_channel_messages(self._channel.id, around=around, before=before, after=after, limit=limit)
        data = await resp.json()
        messages = []
        for message in data:
            messages.append(self._add(message))
        return messages

    async def bulk_delete(self, messages):
        messages = {message.id for message in messages}
        rest = self._client.reat
        await rest.bulk_delete_messages(self._channel.id, messages)

    async def fetch_pins(self):
        rest = self._client.reat
        await rest.get_pinned_message(self._channel.id)