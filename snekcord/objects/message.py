from __future__ import annotations

import enum
from datetime import datetime
from types import NoneType
from typing import Optional

from .base import SnowflakeObject
from .. import json
from ..builders import JSONBuilder
from ..exceptions import UnknownObjectError
from ..mentions import MessageMentions
from ..rest.endpoints import (
    CROSSPOST_CHANNEL_MESSAGE,
    DELETE_CHANNEL_MESSAGE,
    MODIFY_CHANNEL_MESSAGE,
)
from ..undefined import MaybeUndefined, UndefinedType, undefined

__all__ = ('MessageType', 'MessageFlags', 'Message')


class MessageType(enum.IntEnum):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    CHAT_INPUT_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22
    CONTEXT_MENU_COMMAND = 23


class MessageFlags(enum.IntFlag):
    NONE = 0
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPREDD_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4
    HAS_THREAD = 1 << 5
    EPHEMERAL = 1 << 6
    LOADING = 1 << 7


class Message(SnowflakeObject):
    __slots__ = ('author', 'member', 'webhook', 'application')

    type = json.JSONField('type', MessageType, repr=True)
    flags = json.JSONField('flags', MessageFlags, repr=True)
    content = json.JSONField('content')
    created_at = json.JSONField('timestamp', datetime.fromisoformat)
    edited_at = json.JSONField('edited_timestamp', datetime.fromisoformat)
    tts = json.JSONField('tts')
    # mentions
    # attachments, embeds, reactions
    nonce = json.JSONField('nonce')
    pinned = json.JSONField('pinned')
    # activity
    # message_reference, referenced_message
    # interaction
    # thread
    # components
    # sticker_items

    def __init__(self, *, state):
        super().__init__(state=state)
        self.author = None
        self.member = None
        # self.webhook = self.client.webhooks.wrap_id(None)
        # self.application = self.client.applications.wrap_id(None)

    @property
    def channel(self):
        return self.state.channel

    @property
    def guild(self):
        return self.channel.guild

    async def crosspost(self) -> Message:
        data = await self.client.rest.request(
            CROSSPOST_CHANNEL_MESSAGE, channel_id=self.channel.id, message_id=self.id
        )
        assert isinstance(data, dict)

        return await self.state.upsert(data)

    async def modify(
        self,
        *,
        content: MaybeUndefined[Optional[str]] = undefined,
        embeds=undefined,
        flags: MaybeUndefined[Optional[MessageFlags]] = undefined,
        mentions: MaybeUndefined[Optional[MessageMentions]] = undefined,
        components=undefined,
        attachments=undefined,
    ) -> None:
        body = JSONBuilder()

        body.str('content', content, nullable=True)
        body.int('flags', flags, nullable=True)

        if not isinstance(mentions, (MessageMentions, UndefinedType, NoneType)):
            cls = mentions.__class__
            raise TypeError(
                f'mentions should be MessageMentions, undefined or None, got {cls.__name__!r}'
            )

        body.set('allowed_mentions', mentions, transformer=MessageMentions.to_dict)

        data = await self.client.rest.request(
            MODIFY_CHANNEL_MESSAGE, channel_id=self.channel.id, message_id=self.id, json=body
        )
        assert isinstance(data, dict)

        return await self.state.upsert(data)

    async def delete(self) -> None:
        await self.client.rest.request(
            DELETE_CHANNEL_MESSAGE, channel_id=self.channel.id, message_id=self.id
        )

    async def _update_author(self, data):
        self.author = await self.client.users.upsert(data)

    async def _update_member(self, data):
        try:
            guild = self.guild.unwrap()
        except UnknownObjectError:
            self.member = None
        else:
            self.member = await guild.members.upsert(data)
