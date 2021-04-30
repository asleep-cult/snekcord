from datetime import datetime
from typing import Any, Union

from ..states.base import BaseState, BaseSubState
from ..templates.base import BaseTemplate
from ..utils.json import JsonObject
from ..utils.snowflake import Snowflake

__all__ = ('BaseObject',)


class BaseObject(JsonObject, template=BaseTemplate):
    __slots__ = ('_state', 'cached', 'deleted')

    _state: Union[BaseState, BaseSubState]
    id: Snowflake
    cached: bool
    deleted: bool

    @property
    def datetime(self) -> datetime:
        return self.id.datetime

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> Snowflake:
        return self.id
