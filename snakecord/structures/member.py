from ..utils import JsonField, JsonStructure


class GuildMember(JsonStructure, base=True):
    __json_fields__ = {
        '_user': JsonField('user'),
        'nick': JsonField('nick'),
        '_roles': JsonField('roles'),
        'joined_at': JsonField('joined_at'),
        'premium_since': JsonField('premium_since'),
        'deaf': JsonField('deaf'),
        'mute': JsonField('mute'),
        'pending': JsonField('pending'),
    }
