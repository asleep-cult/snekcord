from typing import List

from ..utils import JsonField, JsonArray, JsonStructure, Json


class GuildMember(JsonStructure, base=False):
    __json_fields__ = {
        '_user': JsonField('user'),
        'nick': JsonField('nick'),
        '_roles': JsonArray('roles'),
        'joined_at': JsonField('joined_at'),
        'premium_since': JsonField('premium_since'),
        'deaf': JsonField('deaf'),
        'mute': JsonField('mute'),
        'pending': JsonField('pending'),
    }

    _user: Json
    nick: str
    _roles: List[Json]
    joined_at: str
    premium_since: str
    deaf: bool
    mute: bool
    pending: bool
