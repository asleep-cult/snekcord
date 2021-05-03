from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import datetime

from .base import BaseTemplate
from ..utils.json import JsonArray, JsonField, JsonTemplate
from ..utils.snowflake import Snowflake

if TYPE_CHECKING:
    from ..objects.message import Message

MessageTemplate: JsonTemplate[Message] = JsonTemplate(
    channel_id=JsonField('channel_id', Snowflake, str),
    guild_id=JsonField('guild_id', Snowflake, str),
    _author=JsonField('author'),
    _member=JsonField('member', default=dict),
    content=JsonField('content'),
    edited_timestamp=JsonField(
        'edited_timestamp', datetime.fromisoformat, datetime.isoformat),
    tts=JsonField('tts'),
    mention_everyone=JsonField('mention_everyone'),
    _mentions=JsonArray('mentions'),
    _mention_roles=JsonArray('mention_roles'),
    _mention_channels=JsonArray('mention_channels'),
    _attachments=JsonArray('attachments'),
    _embeds=JsonArray('embeds'),
    _reactions=JsonArray('reactions'),
    nonce=JsonField('nonce'),
    pinned=JsonField('pinned'),
    webhook_id=JsonField('webhook_id'),
    type=JsonField('type'),
    _activity=JsonField('activity'),
    application=JsonField('application'),
    _message_reference=JsonField('message_reference'),
    flags=JsonField('flags'),
    _stickers=JsonArray('stickers'),
    _referenced_message=JsonField('referenced_message'),
    _interaction=JsonField('interaction'),
    __extends__=(BaseTemplate,)
)
