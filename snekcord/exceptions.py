from __future__ import annotations

import typing
from http import HTTPStatus

from .json import JSONObject, JSONType, json_get
from .snowflake import Snowflake

if typing.TYPE_CHECKING:
    import aiohttp

    from .rest import RESTSession
    from .states import MemberID
    from .websockets import Shard


class IncompleteDataError(Exception):
    def __init__(self, model: object, name: str) -> None:
        self.model = model
        self.name = name

    def __str__(self):
        return f'{self.model.__class__.__name__!r} is missing {self.name!r}'


class UnknownSnowflakeError(Exception):
    def __init__(self, id: Snowflake) -> None:
        self.id = id

    def __str__(self):
        return f'Object with id {self.id} is not cached'


class UnknownCodeError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code

    def __str__(self) -> str:
        return f'Object with code {self.code} is not cached'


class UnknownMemberError(Exception):
    def __init__(self, id: MemberID) -> None:
        self.id = id

    def __str__(self) -> str:
        return f'Member with id {self.id!r} is not cached'


class ShardConnectError(Exception):
    def __init__(self, message: str, shard: Shard) -> None:
        self.message = message
        self.shard = shard

    def __str__(self) -> str:
        return self.message


class AuthenticationFailedError(Exception):
    def __init__(self, shard: Shard) -> None:
        self.shard = shard
        self.token = self.shard.token

    def __str__(self):
        return 'Shard failed to authenticate. Make sure you are using the correct token.'


class DisallowedIntentsError(Exception):
    def __init__(self, shard: Shard) -> None:
        self.shard = shard

    def __str__(self):
        return 'Shard enabled intents that are disallowed.'


class ShardCloseError(Exception):
    def __init__(self, code: int, shard: Shard) -> None:
        self.code = code
        self.shard = shard

    def __str__(self) -> str:
        return f'Shard closed due to error ({self.code})'


class PendingCancellationError(Exception):
    def __str__(self) -> str:
        return 'A cancellation is pending'


class RESTError(Exception):
    def __init__(
        self,
        session: RESTSession,
        method: str,
        url: str,
        response: aiohttp.ClientResponse,
        data: typing.Optional[typing.Union[JSONType, bytes]],
    ) -> None:
        self.session = session
        self.method = method
        self.url = url
        self.response = response
        self.data = data

    @property
    def status(self) -> HTTPStatus:
        return HTTPStatus(self.response.status)

    def is_unauthorized(self):
        return self.status is HTTPStatus.UNAUTHORIZED

    def is_forbidden(self):
        return self.status is HTTPStatus.FORBIDDEN

    def is_not_found(self):
        return self.status is HTTPStatus.NOT_FOUND

    def is_too_many_requests(self):
        return self.status is HTTPStatus.TOO_MANY_REQUESTS

    def is_bad_gateway(self):
        return self.status is HTTPStatus.BAD_GATEWAY

    def format_error(
        self, error: JSONObject, keys: typing.Optional[typing.Tuple[str]] = None
    ) -> str:
        message = error.get('message', '<missing message>')
        code = error.get('code', '<missing code>')

        if keys is not None:
            key = '.'.join(str(key) for key in keys)
            return f'\n{key}: {message} ({code})'

        return f'\n{message} ({code})'

    def __str__(self):
        string = f'[{self.method} {self.url} => {self.status} {self.status.phrase}]'

        if isinstance(self.data, dict):
            if 'errors' in self.data:
                errors = json_get(self.data, 'errors', JSONObject)
                stack: typing.List[typing.Tuple[typing.Tuple[str, ...], JSONObject]] = []

                for key in errors:
                    if key == '_errors':
                        values = json_get(errors, '_errors', typing.List[JSONObject])
                        for error in values:
                            string += self.format_error(error)
                    else:
                        value = json_get(errors, key, JSONObject)
                        stack.append(((key,), value))

                while stack:
                    keys, errors = stack.pop()

                    for key in errors:
                        if key == '_errors':
                            values = json_get(errors, '_errors', typing.List[JSONObject])
                            for error in values:
                                string += self.format_error(error)
                        else:
                            value = json_get(errors, key, JSONObject)
                            stack.append((keys + (key,), value))

        return string
