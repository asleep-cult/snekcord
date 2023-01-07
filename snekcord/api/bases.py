from __future__ import annotations

import inspect
import typing

from ..json import JSONObject, JSONType

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..rest.endpoints import APIEndpoint, CDNEndpoint
    from ..streams import ResponseReadStream
    from ..websockets import Shard

EventCallbackT = typing.Callable[
    [Shard, JSONObject], typing.Coroutine[typing.Any, typing.Any, None]
]


class BaseAPI:
    """The base class for all object APIs.
    Object APIs process all raw data from Discord's REST API and Gateway.
    """

    def __init__(self, *, client: Client) -> None:
        self.client = client
        self.events: typing.Dict[str, EventCallbackT] = {}

        for name, member in inspect.getmembers(self, inspect.isfunction):
            if name.startswith('on_'):
                self.events[name[3:]] = member

    async def request_api(
        self, endpoint: APIEndpoint, **kwargs: typing.Any
    ) -> typing.Union[JSONType, bytes]:
        return await self.client.rest.request_api(endpoint, **kwargs)

    async def request_cdn(self, endpoint: CDNEndpoint, **kwargs: typing.Any) -> ResponseReadStream:
        return await self.client.rest.request_cdn(endpoint, **kwargs)
