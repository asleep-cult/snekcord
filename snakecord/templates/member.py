from .template import BaseTemplate
from ..utils.json import JsonArray, JsonField, JsonTemplate

GuildMemberTemplate = JsonTemplate(
    _user=JsonField('user'),
    nick=JsonField('nick'),
    _roles=JsonArray('roles'),
    joined_at=JsonField('joined_at'),
    premium_since=JsonField('premium_since'),
    deaf=JsonField('deaf'),
    mute=JsonField('mute'),
    pending=JsonField('pending'),
    __extends__=(BaseTemplate,)
)
