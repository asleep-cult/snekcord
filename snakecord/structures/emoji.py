from .base import BaseObject
from ..utils import JsonArray, JsonField


class GuildEmoji(BaseObject, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
        '_roles': JsonArray('roles'),
        '_user': JsonField('user'),
        'required_colons': JsonField('required_colons'),
        'managed': JsonField('managed'),
        'animated': JsonField('animated'),
        'available': JsonField('available'),
    }
