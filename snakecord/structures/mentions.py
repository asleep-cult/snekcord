from typing import List

from .base import BaseObject
from ..utils import JsonArray, JsonField, JsonStructure, Snowflake, Json


class ChannelMention(BaseObject, base=False):
    __json_fields__ = {
        'guild_id': JsonField('int', Snowflake, str),
        'type': JsonField('type'),
        'name': JsonField('name'),
    }

    guild_id: Snowflake
    type: int
    name: str


class AllowedMentions(JsonStructure, base=False):
    __json_fields__ = {
        'parse': JsonArray('parse'),
        '_roles': JsonArray('roles', Snowflake, str),
        '_users': JsonArray('users', Snowflake, str),
        '_replied_user': JsonField('replied_user'),
    }

    parse: List[str]
    _roles: List[Snowflake]
    _users: List[Snowflake]
    _replied_user: Json
