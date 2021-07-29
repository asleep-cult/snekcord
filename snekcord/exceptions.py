from http import HTTPStatus

__all__ = ('PartialObjectError', 'RestError')


class PartialObjectError(AttributeError):
    pass


class RestError(Exception):
    def __init__(self, session, method, url, response, data):
        self.session = session
        self.method = method
        self.url = url
        self.response = response
        self.status = HTTPStatus(response.status_code)
        self.data = data
        super().__init__(self.get_message())

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

        for keys, errors in self.get_errors():
            for error in errors:
                keys = self.format_keys(keys)
                message += f'\n{keys}: {error.get("message")} {error.get("code")}'

        return message
