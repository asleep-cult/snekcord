from __future__ import annotations

import typing as t
from datetime import datetime

from ..states.basestate import BaseState
from ..utils import JsonObject, JsonTemplate

__all__ = ('BaseObject',)

T = t.TypeVar('T')
IDT = t.TypeVar('IDT')

BaseTemplate: JsonTemplate


class BaseObject(t.Generic[IDT], JsonObject, template=BaseTemplate):
    id: IDT | None

    state: BaseState[t.Any, IDT, t.Any]
    cached: bool
    deleted: bool
    deleted_at: datetime | None

    def __init__(self, *, state: BaseState[t.Any, IDT, t.Any]) -> None: ...

    def __hash__(self) -> int: ...

    def cache(self) -> None: ...

    def uncache(self) -> None: ...

    async def fetch(self: T) -> T: ...
