from __future__ import annotations

from datetime import datetime
from typing import Generic, Optional, TypeVar

from ..states.basestate import BaseState
from ..utils import JsonObject, JsonTemplate, Snowflake


BaseTemplate: JsonTemplate = ...

_T = TypeVar('_T')


class BaseObject(JsonObject, Generic[_T], template=BaseTemplate):
    id: Optional[_T]
    state: BaseState[_T]
    cached: bool
    deleted: bool
    deleted_at: Optional[datetime]

    def __init__(self, *, state: BaseState[_T]) -> None: ...

    def __hash__(self) -> int: ...

    def __repr__(self) -> str: ...

    def _delete(self) -> None: ...

    def cache(self) -> None: ...

    def uncache(self) -> None: ...

    async def fetch(self: BaseObject[_T]) -> BaseObject[_T]: ...


BaseSnowflakeObject = BaseObject[Snowflake]
