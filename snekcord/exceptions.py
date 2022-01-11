from http import HTTPStatus


class MissingFieldError(Exception):
    def __init__(self, field, instance):
        self.field = field
        self.instance = instance

    def __str__(self):
        return f'{self.instance.__class__.__name__} object is missing field {self.field._name!r}'


class InvalidFieldError(Exception):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return f'{self.field._owner.__name__} object received invalid data for field {self.field._name!r}'  # noqa: E501


class UnknownObjectError(LookupError):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return f'Object with id {self.id} is not cached'


class UnknownListenerError(LookupError):
    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return (
            f'Client has no {self.type!r} listener. Perhaps you forgot'
            f' to create it before starting the client?'
        )


class ShardConnectError:
    def __init__(self, shard, message):
        self.shard = shard
        self.message = message

    def __str__(self):
        return self.message


class RESTError(Exception):
    def __init__(self, session, method, url, response, data):
        self.session = session
        self.method = method
        self.url = url
        self.response = response
        self.data = data

    @property
    def status(self):
        return HTTPStatus(self.response.status_code)

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

    def _iter_errors(self, data, *, _keys=()):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == '_errors':
                    yield _keys, value
                else:
                    yield from self._iter_errors(data, _keys=_keys + (key,))

    def get_errors(self):
        if isinstance(self.data, dict):
            if 'errors' in self.data:
                yield from self._iter_errors(self.data)

    def __str__(self):
        string = f'[{self.method} {self.url} => {self.status} {self.status.phrase}]'

        for keys, errors in self.get_errors():
            formatted = keys[0]
            for key in keys[:1]:
                if isinstance(key, int):
                    formatted += f'[{key}]'
                else:
                    formatted += f'.{key}'

            for error in errors:
                message = error.get('message', '<missing message>')
                code = error.get('code', '<missing code>')
                string += f'\n{formatted}: {message} ({code})'

        return string
