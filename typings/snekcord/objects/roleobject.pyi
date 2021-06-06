from typing import Any
from .baseobject import BaseObject
from .guildobject import Guild
from ..utils import JsonObject, JsonTemplate, Snowflake

class RoleTags(JsonObject):
    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: Any  # ?

RoleTemplate: JsonTemplate = ...

class Role(BaseObject[Snowflake]):
    guild: Guild
