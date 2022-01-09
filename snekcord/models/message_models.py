import enum
from datetime import datetime

from .base_models import BaseModel
from .. import json

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


class Message(BaseModel):
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

    def __init__(self, *, state, author, member):
        super().__init__(state=state)
        self.author = author
        self.member = member
        self.webhook = self.client.webhooks.wrap_id(None)
        self.application = self.client.applications.wrap_id(None)

    @property
    def channel(self):
        return self.state.channel

    @property
    def guild(self):
        return self.channel.guild
