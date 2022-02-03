from __future__ import annotations

import typing

import httpx

from . import hdrs
from ..exceptions import RESTError
from ..json import load_json

if typing.TYPE_CHECKING:
    from .endpoints import RESTEndpoint
    from ..json import JSONType
    from ..auth import Authorization

BASE_API_URL = 'https://discord.com/api/v9'
BASE_CDN_URL = 'https://cdn.discordapp.com'


class RESTSession:
    def __init__(self, *, authorization: Authorization, **kwargs: typing.Any) -> None:
        self.authorization = authorization

        try:
            self.api = kwargs.pop('api').rstrip('/')
        except KeyError:
            self.api = BASE_API_URL

        try:
            self.cdn = kwargs.pop('cdn').rstrip('/')
        except KeyError:
            self.cdn = BASE_CDN_URL

        try:
            self.headers = httpx.Headers(kwargs.pop('headers'))
        except KeyError:
            self.headers = httpx.Headers()

        self.headers[hdrs.AUTHORIZATION] = self.authorization.to_token()

        kwargs.setdefault('timeout', None)
        self.client = httpx.AsyncClient(**kwargs)

    async def request(
        self, endpoint: RESTEndpoint, **kwargs: typing.Any
    ) -> typing.Union[bytes, JSONType]:
        keywords = {keyword: kwargs.pop(keyword) for keyword in endpoint.keywords}

        try:
            headers = kwargs['headers']
        except KeyError:
            kwargs['headers'] = self.headers
        else:
            headers.update(self.headers)

        url = self.api + endpoint.path.format_map(keywords)
        response: typing.Any = await self.client.request(endpoint.method, url, **kwargs)

        data = await response.aread()
        if response.headers.get(hdrs.CONTENT_TYPE) == hdrs.APPLICATION_JSON:
            data = load_json(data)

        if response.status_code >= 400:
            raise RESTError(self, endpoint.method, url, response, data)

        return data

    async def aclose(self) -> None:
        await self.client.aclose()
