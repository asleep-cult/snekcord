from __future__ import annotations

import typing as t
from datetime import datetime

from ..states.basestate import BaseState
from ..utils import JsonField, JsonObject

__all__ = ('BaseObject',)

T = t.TypeVar('T')
IDT = t.TypeVar('IDT')


class BaseObject(t.Generic[IDT], JsonObject):
    id: t.ClassVar[JsonField[IDT]]

    state: BaseState[t.Any, IDT, t.Any]
    cached: bool
    deleted: bool
    deleted_at: datetime | None

    def __init__(self, *, state: BaseState[t.Any, IDT, t.Any]) -> None: ...

    def __hash__(self) -> int: ...

    def cache(self) -> None: ...

    def uncache(self) -> None: ...

    async def fetch(self: T) -> T: ...
