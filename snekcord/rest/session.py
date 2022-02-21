from __future__ import annotations

import typing

import aiohttp

from multidict import CIMultiDict

from . import hdrs
from .endpoints import APIEndpoint, CDNEndpoint
from ..exceptions import RESTError
from ..json import dump_json, load_json
from ..streams import ResponseReadStream

if typing.TYPE_CHECKING:
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

        self.api = api if api is not None else BASE_API_URL
        self.cdn = cdn if cdn is not None else BASE_CDN_URL

        if headers is not None:
            self.headers = CIMultiDict(headers)
        else:
            self.headers = CIMultiDict()

        self.headers[hdrs.AUTHORIZATION] = self.authorization.to_token()

        self.session: typing.Optional[aiohttp.ClientSession] = None

    def create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(json_serialize=dump_json)

    async def request_api(
        self, endpoint: APIEndpoint, **kwargs: typing.Any
    ) -> typing.Union[bytes, JSONType]:
        if self.session is None:
            self.session = self.create_session()

        try:
            headers = kwargs.pop('headers')
        except KeyError:
            headers = self.headers
        else:
            headers.update(self.headers)

        params = kwargs.pop('params', None)
        json = kwargs.pop('json', None)

        url = endpoint.url(self.api, **kwargs)
        response = await self.session.request(
            endpoint.method, url, params=params, headers=headers, json=json
        )

        data = await response.read()
        if response.headers.get(hdrs.CONTENT_TYPE) == hdrs.APPLICATION_JSON:
            data = load_json(data)

        if not response.ok:
            raise RESTError(self, endpoint.method, url, response, data)

        return data

    async def request_cdn(self, endpoint: CDNEndpoint, **kwargs: typing.Any) -> ResponseReadStream:
        if self.session is None:
            self.session = self.create_session()

        url = endpoint.url(self.cdn, **kwargs)
        response = await self.session.request('GET', url)

        if not response.ok:
            raise RESTError(self, 'GET', url, response, None)

        return ResponseReadStream(response)

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
