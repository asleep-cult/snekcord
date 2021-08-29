from http import HTTPStatus

__all__ = ('MissingFieldError', 'HTTPError')


class MissingFieldError(AttributeError):
    def __init__(self, field):
        super().__init__()
        self.field = field

    def __str__(self):
        return f'{self.field.owner.__name__} object is missing field {self.field.name}'


class HTTPError(Exception):
    def __init__(self, session, method, url, response, data):
        super().__init__()
        self.session = session
        self.method = method
        self.url = url
        self.response = response
        self.status = HTTPStatus(response.status_code)
        self.data = data

    def __str__(self):
        return self.get_message()

    def _iter_errors(self, data, keys=()):
        if isinstance(data, dict):
            if '_errors' in data:
                yield keys, data['_errors']
            else:
                for key, value in data.items():
                    yield from self._iter_errors(value, keys + (key,))

    def get_errors(self):
        if isinstance(self.data, dict):
            if 'errors' in self.data:
                yield from self._iter_errors(self.data['errors'])

    def format_keys(self, keys):
        keys = iter(keys)
        value = next(keys)

        for key in keys:
            if key.isdigit():
                value += f'[{key}]'
            else:
                value += f'.{key}'

        return value

    def get_message(self):
        message = f'[{self.method} {self.url} => {self.status} {self.status.phrase}]'

        if self.session.is_dapi(self.url):
            for keys, errors in self.get_errors():
                for error in errors:
                    keys = self.format_keys(keys)
                    message += f'\n{keys}: {error.get("message")} {error.get("code")}'

        return message
