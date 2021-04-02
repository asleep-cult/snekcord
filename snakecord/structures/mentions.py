from .base import BaseObject
from ..utils import JsonArray, JsonField, JsonStructure, Snowflake


class ChannelMention(BaseObject, base=False):
    __json_fields__ = {
        'guild_id': JsonField('int', int, str),
        'type': JsonField('int'),
        'name': JsonField('name'),
    }


class AllowedMentions(JsonStructure, base=False):
    __json_fields__ = {
        'parse': JsonArray('parse'),
        'roles': JsonArray('roles', Snowflake, str),
        'users': JsonArray('users', Snowflake, str),
        'replied_user': JsonField('replied_user'),
    }
