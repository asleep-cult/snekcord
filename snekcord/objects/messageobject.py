from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject, BaseTemplate
from .embedobject import Embed
from .. import rest
from ..utils import (Bitset, Enum, Flag, JsonArray, JsonField, JsonTemplate,
                     Snowflake)

__all__ = ('MessageType', 'MessageFlags', 'Message')

if t.TYPE_CHECKING:
    from ..objects import (
        DMChannel, Guild, GuildChannel, GuildMember, User
    )
    from ..states import MessageState, ReactionsState
    from ..typing import Json


class MessageType(Enum[int]):
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
    edited_timestamp=JsonField(
        'edited_timestamp',
        datetime.fromisoformat,
        datetime.isoformat
    ),
    tts=JsonField('tts'),
    mention_everyone=JsonField('mention_everyone'),
    _mentions=JsonArray('mentions'),
    _mention_roles=JsonArray('mention_roles'),
    _mention_channels=JsonArray('mention_channels'),
    _attachments=JsonArray('attachments'),
    embeds=JsonArray('embeds', object=Embed),
    nonce=JsonField('nonce'),
    pinned=JsonField('pinned'),
    webhook_id=JsonField(
        'webhook_id',
        Snowflake,
        str
    ),
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

    if t.TYPE_CHECKING:
        state: MessageState
        reactions: ReactionsState
        author: t.Optional[User]
        member: t.Optional[GuildMember]
        channel_id: Snowflake
        guild_id: t.Optional[Snowflake]
        content: str
        edited_timestamp: t.Optional[datetime]
        tts: bool
        mention_everyone: bool
        embeds: t.List[Embed]
        nonce: t.Optional[t.Union[int, str]]
        pinned: bool
        type: MessageType
        application: t.Optional[Json]
        flags: t.Optional[MessageFlags]

    def __init__(self, *, state: MessageState) -> None:
        super().__init__(state=state)
        self.author = None
        self.member = None
        self.reactions = self.state.client.get_class(  # type: ignore
            'ReactionsState')(  # type: ignore
            client=self.state.client, message=self)  # type: ignore

    @property
    def channel(self) -> t.Union[GuildChannel, DMChannel]:
        return self.state.channel

    @property
    def guild(self) -> t.Optional[Guild]:
        return getattr(self.channel, 'guild', None)

    async def crosspost(self) -> Message:
        data = await rest.crosspost_message.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.channel.id, message_id=self.id))

        return self.state.upsert(data)

    async def delete(self) -> None:
        await rest.delete_message.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.channel.id, message_id=self.id))

    def update(   # type: ignore
        self, data: Json, *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        author = data.get('author')
        if author is not None:
            self.author = self.state.client.users.upsert(author)

            guild = self.guild
            member = data.get('member')
            if member is not None and guild is not None:
                member['user'] = author
                self.member = guild.members.upsert(member)

        reactions = data.get('reactions')
        if reactions is not None:
            self.reactions.clear()
            self.reactions.upsert_many(reactions)
