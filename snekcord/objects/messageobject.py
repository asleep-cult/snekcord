from .baseobject import BaseObject, BaseTemplate
from .embedobject import Embed
from .. import rest
from ..utils import (Bitset, Enum, Flag, JsonArray, JsonField, JsonTemplate,
                     Snowflake)

__all__ = ('Message',)


class MessageType(Enum, type=int):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PERMIUM_GUILD_SUBSCRIPTION = 8
    USER_PERMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    APPLICATION_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22


class MessageFlags(Bitset):
    CROSSPOSTED = Flag(0)
    IS_CROSSPOST = Flag(1)
    SUPPRESS_EMBEDS = Flag(2)
    SOURCE_MESSAGE_DELETED = Flag(3)
    URGENT = Flag(4)
    HAS_THREAD = Flag(5)
    EPHEMERAL = Flag(7)
    LOADING = Flag(8)


MessageTemplate = JsonTemplate(
    channel_id=JsonField('channel_id', Snowflake, str),
    guild_id=JsonField('guild_id', Snowflake, str),
    content=JsonField('content'),
    edited_timestamp=JsonField('edited_timestamp'),
    tts=JsonField('tts'),
    mention_everyone=JsonField('mention_everyone'),
    _mentions=JsonArray('mentions'),
    _mention_roles=JsonArray('mention_roles'),
    _mention_channels=JsonArray('mention_channels'),
    _attachments=JsonArray('attachments'),
    embeds=JsonArray('embeds', object=Embed),
    nonce=JsonField('nonce'),
    pinned=JsonField('pinned'),
    webhook_id=JsonField('webhook_id'),
    type=JsonField(
        'type',
        MessageType.get_enum,
        MessageType.get_value
    ),
    _activity=JsonField('activity'),
    application=JsonField('application'),
    _message_reference=JsonField('message_reference'),
    flags=JsonField(
        'flags',
        MessageFlags.from_value,
        MessageFlags.get_value
    ),
    _stickers=JsonArray('stickers'),
    _referenced_message=JsonField('referenced_message'),
    _interaction=JsonField('interaction'),
    __extends__=(BaseTemplate,)
)


class Message(BaseObject, template=MessageTemplate):
    __slots__ = ('author', 'member', 'reactions')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.author = None
        self.member = None
        self.reactions = self.state.manager.get_class('ReactionsState')(
            manager=self.state.manager, message=self)

    @property
    def channel(self):
        return self.state.channel

    @property
    def guild(self):
        return getattr(self.channel, 'guild', None)

    async def crosspost(self):
        data = await rest.crosspost_message.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.channel.id, message_id=self.id))

        return self.state.upsert(data)

    async def delete(self):
        await rest.delete_message.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.channel.id, message_id=self.id))

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        author = data.get('author')
        if author is not None:
            self.author = self.state.manager.users.upsert(author)

            guild = self.guild
            member = data.get('member')
            if member is not None and guild is not None:
                member['user'] = author
                self.member = guild.members.upsert(member)

        reactions = data.get('reactions')
        if reactions is not None:
            self.reactions.clear()
            self.reactions.upsert_many(reactions)
