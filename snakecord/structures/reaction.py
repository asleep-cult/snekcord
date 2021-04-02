from ..utils import JsonField, JsonStructure


class Reaction(JsonStructure, base=True):
    __json_fields__ = {
        'count': JsonField('count'),
        'me': JsonField('me'),
        'emoji': JsonField('emoji'),
    }
