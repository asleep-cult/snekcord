from __future__ import annotations

import asyncio
import typing as t

from httpx import AsyncClient, Response

from ..clients.client import Client
from ..typedefs import Json

__all__ = ('HTTPError', 'RestSession')


class HTTPError(Exception):
    response: Response

    def __init__(self, msg: str, response: Response) -> None: ...


class RestSession(AsyncClient):
    loop: asyncio.AbstractEventLoop
    client: Client
    authorization: str
    api_version: str
    global_headers: Json

    def __init__(self, client: Client, *args: t.Any,
                 **kwargs: t.Any) -> None: ...

    async def request(self, method: str, url: str, fmt: Json,
                      *args: t.Any, **kwargs: t.Any) -> Json | bytes: ...
