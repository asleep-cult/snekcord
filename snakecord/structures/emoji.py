from typing import List

from .base import BaseObject
from ..utils import JsonArray, JsonField, Json


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

    name: str
    _roles: List[Json]
    _user: Json
    required_colons: bool
    managed: bool
    animated: bool
    available: bool
