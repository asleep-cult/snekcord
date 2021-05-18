from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional, TypeVar

from ..states.basestate import BaseState
from ..utils import JsonObject, JsonTemplate, Snowflake

BaseTemplate: JsonTemplate

T = TypeVar('T')


class BaseObject(JsonObject):
    __slots__: ClassVar[tuple[str, ...]]
    id: Optional[int]
    state: BaseState[Snowflake, BaseObject]
    cached: bool
    deleted: bool
    deleted_at: Optional[datetime]

    def __json_init__(self, *,
                      state: BaseState[Snowflake, BaseObject]) -> None: ...

    def __hash__(self) -> int: ...

    def __repr__(self) -> str: ...

    def _delete(self) -> None: ...

    def cache(self) -> None: ...

    def uncache(self) -> None: ...

    async def fetch(self: T) -> T: ...
