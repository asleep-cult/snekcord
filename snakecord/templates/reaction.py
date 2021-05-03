from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils.json import JsonField, JsonTemplate

if TYPE_CHECKING:
    from ..objects.reaction import Reaction

ReactionTemplate: JsonTemplate[Reaction] = JsonTemplate(
    count=JsonField('count'),
    me=JsonField('me'),
    emoji=JsonField('emoji')
)
