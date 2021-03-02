from ..utils import JsonField, JsonStructure


class Reaction(JsonStructure):
    __json_fields__ = {
        'count': JsonField('count'),
        'me': JsonField('me'),
        'emoji': JsonField('emoji'),
    }
