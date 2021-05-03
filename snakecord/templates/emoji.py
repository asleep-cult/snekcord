from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseTemplate
from ..utils.json import JsonArray, JsonField, JsonTemplate

if TYPE_CHECKING:
    from ..objects.emoji import GuildEmoji

GuildEmojiTemplate: JsonTemplate[GuildEmoji] = JsonTemplate(
    name=JsonField('name'),
    _roles=JsonArray('roles'),
    _user=JsonField('user'),
    required_colons=JsonField('required_colons'),
    managed=JsonField('managed'),
    animated=JsonField('animated'),
    available=JsonField('available'),
    __extends__=(BaseTemplate,)
)
