from typing import Any, Dict, Type

from .basestate import BaseState
from ..objects.guildobject import Guild
from ..utils import JsonTemplate, Snowflake

class GuildState(BaseState[Snowflake]):
    __key_transformer__ = Snowflake.try_snowflake
    __guild_class__: Type[Guild]
    __guild_template_class__: JsonTemplate

    def upsert(self, data: Dict[str, Any]) -> Guild: ...
    def new_template(self, data: Dict[str, Any]) -> None: ...