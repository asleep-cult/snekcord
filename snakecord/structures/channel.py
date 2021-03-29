from .base import BaseObject
from ..utils import JsonArray, JsonField, JsonStructure, Snowflake


class GuildChannel(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'guild_id': JsonField('guild_id', Snowflake, str),
        '_permission_overwrites': JsonArray('permission_overwrites'),
        'position': JsonField('position'),
        'nsfw': JsonField('nsfw'),
        'parent_id': JsonField('parent_id', Snowflake, str),
        'type': JsonField('type'),
    }


class TextChannel(JsonStructure):
    __json_fields__ = {
        'topic': JsonField('topic'),
        'slowmode': JsonField('rate_limit_per_user'),
        'last_message_id': JsonField('last_message_id', Snowflake, str),
    }


class VoiceChannel(JsonStructure):
    __json_fields__ = {
        'bitrate': JsonField('bitrate'),
        'user_limit': JsonField('user_limit'),
    }


class DMChannel(JsonStructure):
    __json_fields__ = {
        'last_message_id': JsonField('last_message_id', Snowflake, str),
        'type': JsonField('type'),
        '_recipients': JsonArray('recipients'),
    }
