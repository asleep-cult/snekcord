from ..utils import JsonField, JsonStructure, Json


class Reaction(JsonStructure, base=False):
    __json_fields__ = {
        'count': JsonField('count'),
        'me': JsonField('me'),
        'emoji': JsonField('emoji'),
    }

    count: int
    me: bool
    emoji: Json
