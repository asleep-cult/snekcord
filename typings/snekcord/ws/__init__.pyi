import asyncio
from typing import Any, Type, TypeVar

from ..manager import Manager

_T = TypeVar('_T')

class WebSocketWorker:
    loop: asyncio.AbstractEventLoop
    manager: Manager
    def __init__(self, *, manager: Manager, timeout: float) -> None: ...
    async def create_connection(self, cls: Type[_T], *args: Any, **kwargs: Any) -> _T: ...