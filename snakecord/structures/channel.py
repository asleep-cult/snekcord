from typing import List

from .base import BaseObject
from ..enums import ChannelType
from ..utils import JsonArray, JsonField, JsonStructure, Snowflake, Json


class GuildChannel(BaseObject, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
        'guild_id': JsonField('guild_id', Snowflake, str),
        '_permission_overwrites': JsonArray('permission_overwrites'),
        'position': JsonField('position'),
        'nsfw': JsonField('nsfw'),
        'parent_id': JsonField('parent_id', Snowflake, str),
        'type': JsonField('type'),
    }

    name: str
    guild_id: Snowflake
    _permission_overwrites: List[Json]
    position: int
    nsfw: bool
    parent_id: Snowflake
    type: ChannelType


class TextChannel(JsonStructure, base=False):
    __json_fields__ = {
        'topic': JsonField('topic'),
        'slowmode': JsonField('rate_limit_per_user'),
        'last_message_id': JsonField('last_message_id', Snowflake, str),
    }

    topic: str
    slowmode: int
    last_message_id: Snowflake


class VoiceChannel(JsonStructure, base=False):
    __json_fields__ = {
        'bitrate': JsonField('bitrate'),
        'user_limit': JsonField('user_limit'),
    }

    bitrate: int
    user_limit: int


class DMChannel(BaseObject, base=False):
    __json_fields__ = {
        'last_message_id': JsonField('last_message_id', Snowflake, str),
        'type': JsonField('type'),
        '_recipients': JsonArray('recipients'),
    }

    last_message_id: Snowflake
    type: ChannelType
    _recipients: List[Json]
