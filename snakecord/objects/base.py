from datetime import datetime
from typing import Any

from ..templates.base import BaseTemplate
from ..utils.json import JsonObject
from ..utils.snowflake import Snowflake


class BaseObject(JsonObject, template=BaseTemplate):
    id: Snowflake

    @property
    def datetime(self) -> datetime:
        return self.id.datetime

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> Snowflake:
        return self.id
