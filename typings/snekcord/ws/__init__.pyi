import asyncio
from typing import Any, Type, TypeVar

from ..client import client

_T = TypeVar('_T')

class WebSocketWorker:
    loop: asyncio.AbstractEventLoop
    client: client
    def __init__(self, *, client: client, timeout: float) -> None: ...
    async def create_connection(self, cls: Type[_T], *args: Any, **kwargs: Any) -> _T: ...
