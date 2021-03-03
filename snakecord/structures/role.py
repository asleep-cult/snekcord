from .base import BaseObject
from ..utils import JsonField, JsonStructure, Snowflake


class RoleTag(JsonStructure):
    __json_fields__ = {
        'bot_id': JsonField('bot_id', Snowflake, str),
        'integration_id': JsonField('integration_id', Snowflake, str),
        'premium_subscriber': JsonField('premium_subscriber'),
    }


class Role(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'color': JsonField('color'),
        'hoist': JsonField('hoist'),
        'position': JsonField('position'),
        'permissions': JsonField('permissions'),
        'managed': JsonField('managed'),
        'mentionable': JsonField('mentionable'),
        'tags': JsonField('tags', struct=RoleTag),
    }
