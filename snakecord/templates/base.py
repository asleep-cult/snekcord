from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils.json import JsonField, JsonTemplate
from ..utils.snowflake import Snowflake

if TYPE_CHECKING:
    from ..objects.base import BaseObject

BaseTemplate: JsonTemplate[BaseObject] = JsonTemplate(
    id=JsonField('id', Snowflake, str)
)
