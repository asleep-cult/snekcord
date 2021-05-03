from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseTemplate
from ..utils.json import JsonArray, JsonField, JsonTemplate

if TYPE_CHECKING:
    from ..objects.member import GuildMember

GuildMemberTemplate: JsonTemplate[GuildMember] = JsonTemplate(
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
