import json
from http import HTTPStatus

from httpx import AsyncClient

__all__ = ('HTTPError', 'RestSession')


class HTTPError(Exception):
    def __init__(self, msg, response):
        super().__init__(msg)
        self.response = response


class RestSession(AsyncClient):
    def __init__(self, client, *args, **kwargs):
        self.loop = client.loop
        self.client = client

        self.authorization = self.client.token

        self.global_headers = kwargs.pop('global_headers', {})
        self.global_headers.update({
            'Authorization': self.authorization,
        })

        kwargs['timeout'] = None
        super().__init__(*args, **kwargs)

    def _format_error(self, data, keys=None):
        if '_errors' in data:
            messages = []
            for error in data['_errors']:
                messages.append(f'{error["message"]} (code: {error["code"]})')

            keys = iter(keys)
            name = next(keys)
            for key in keys:
                if key.isnumeric():
                    name += f'[{key}]'
                else:
                    name += f'.{key}'

            yield name, messages
        else:
            if keys is None:
                keys = ()

            for key, value in data.items():
                yield from self._format_error(value, keys + (key,))

    async def request(self, method, url, fmt=None, **kwargs):
        if fmt is not None:
            url = url % fmt

        response = await super().request(method, url, **kwargs)
        await response.aclose()

        data = response.content

        content_type = response.headers.get('content-type')
        if (content_type is not None
                and content_type.lower() == 'application/json'):
            data = json.loads(data)

        status_code = response.status_code
        if status_code >= 400:
            status = HTTPStatus(status_code)

            messages = [f'{method} {url} responded with {status} {status.phrase}']

            if isinstance(data, dict):
                messages.append(f': {data["message"]} (code: {data["code"]})')

                if 'errors' in data:
                    for name, msgs in self._format_error(data['errors']):
                        messages.append(f'\n{name}: {msgs.pop(0)}')

                        for msg in msgs:
                            messages.append((',\n' + ' ' * len(name)) + msg)

            message = ''.join(messages)

            raise HTTPError(message, response)

        return data
