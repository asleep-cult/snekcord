from .template import BaseTemplate
from ..utils.json import JsonArray, JsonField, JsonTemplate

GuildEmojiTemplate = JsonTemplate(
    name=JsonField('name'),
    _roles=JsonArray('roles'),
    _user=JsonField('user'),
    required_colons=JsonField('required_colons'),
    managed=JsonField('managed'),
    animated=JsonField('animated'),
    available=JsonField('available'),
    __extends__=(BaseTemplate,)
)
