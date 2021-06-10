from __future__ import annotations

import json
import typing as t
from http import HTTPStatus

from httpx import AsyncClient, Response

__all__ = ('HTTPError', 'RestSession')

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..typing import Json


class HTTPError(Exception):
    def __init__(self, msg: str, response: Response) -> None:
        super().__init__(msg)
        self.response = response


class RestSession(AsyncClient):
    def __init__(
        self, client: Client, *args: t.Any, **kwargs: t.Any
    ) -> None:
        self.loop = client.loop
        self.client = client

        self.authorization = self.client.token
        self.api_version = self.client.api_version

        self.global_headers = kwargs.pop('global_headers', {})
        self.global_headers.update({
            'Authorization': self.authorization,
        })

        kwargs['timeout'] = None
        super().__init__(*args, **kwargs)  # type: ignore

    async def request(  # type: ignore
        self, method: str, url: str,
        fmt: Json, *args: t.Any, **kwargs: t.Any
    ) -> t.Any:
        response = await super().request(  # type: ignore
            method, url % fmt, *args, **kwargs)
        await response.aclose()

        data = response.content

        content_type: str = response.headers.get(  # type: ignore
            'content-type')
        if (content_type is not None
                and content_type.lower() == 'application/json'):
            data = json.loads(data)

        status_code: int = response.status_code  # type: ignore

        if status_code >= 400:
            status = HTTPStatus(status_code)
            raise HTTPError(
                f'{method} {url} responded with {status} {status.phrase}: '
                f'{data}', response)

        return data
