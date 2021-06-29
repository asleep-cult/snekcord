from __future__ import annotations

import typing as t

from .session import RestSession
from ..typedefs import Json

__all__ = ('HTTPEndpoint',)


class HTTPEndpoint:
    method: str
    url: str
    params: tuple[str, ...]
    json: tuple[str, ...]

    def __init__(self, method: str, url: str, *,
                 params: tuple[str, ...] = ...,
                 json: tuple[str, ...] = ...) -> None: ...

    async def request(self, *, session: RestSession, **kwargs: t.Any) -> Json | bytes: ...
