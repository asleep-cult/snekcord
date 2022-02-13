from __future__ import annotations

import typing

import aiohttp

from multidict import CIMultiDict

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
    headers: CIMultiDict[str]

    def __init__(
        self,
        *,
        authorization: Authorization,
        api: typing.Optional[str] = None,
        cdn: typing.Optional[str] = None,
        headers: typing.Optional[typing.Mapping[str, str]] = None,
    ) -> None:
        self.authorization = authorization

        if api is not None:
            self.api = api
        else:
            self.api = BASE_API_URL

        if cdn is not None:
            self.cdn = cdn
        else:
            self.cdn = BASE_CDN_URL

        if headers is not None:
            self.headers = CIMultiDict(headers)
        else:
            self.headers = CIMultiDict()

        self.headers[hdrs.AUTHORIZATION] = self.authorization.to_token()

        self.client: typing.Optional[aiohttp.ClientSession] = None

    async def request(
        self, endpoint: RESTEndpoint, **kwargs: typing.Any
    ) -> typing.Union[bytes, JSONType]:
        if self.client is None:
            self.client = aiohttp.ClientSession()

        keywords = {keyword: kwargs.pop(keyword) for keyword in endpoint.keywords}

        try:
            headers = kwargs['headers']
        except KeyError:
            kwargs['headers'] = self.headers
        else:
            headers.update(self.headers)

        url = self.api + endpoint.path.format_map(keywords)
        response = await self.client.request(endpoint.method, url, **kwargs)

        data = await response.read()
        if response.headers.get(hdrs.CONTENT_TYPE) == hdrs.APPLICATION_JSON:
            data = load_json(data)

        if response.status >= 400:
            raise RESTError(self, endpoint.method, url, response, data)

        return data

    async def aclose(self) -> None:
        if self.client is not None:
            await self.client.close()
