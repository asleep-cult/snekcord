import asyncio
import json

from httpx import AsyncClient

from .ratelimit import RatelimitBucket
from ..exceptions import RestError

__all__ = ('RestSession',)


class RestSession:
    def __init__(self, client, **kwargs):
        self.loop = client.loop

        self.authorization = client.authorization

        self.headers = kwargs.pop('headers', {})
        self.headers.update({
            'Authorization': self.authorization.to_string(),
        })

        self.ratelimiters = {}

        self.global_ratelimiter = asyncio.Event()
        self.global_ratelimiter.set()

        self.max_retries = kwargs.pop('max_retries', 10)

        kwargs['timeout'] = None
        self.client = AsyncClient(**kwargs)

    async def request(self, method, url, *, keywords=None, **kwargs):
        ratelimiter = RatelimitBucket.from_request(self.ratelimiters, method, url, keywords)

        if keywords is not None:
            url = url.format(**keywords)

        headers = kwargs.setdefault('headers', {})
        headers.update(self.headers)

        async with ratelimiter:
            for _ in range(self.max_retries):
                await self.global_ratelimiter.wait()

                response = await self.client.request(method, url, **kwargs)
                ratelimiter.update(response)

                if response.status_code == 429:
                    if response.headers['X-RateLimit-Global']:
                        self.global_ratelimiter.clear()
                        self.loop.call_later(
                            float(response.headers['Retry-After']), self.global_ratelimiter.set
                        )
                    else:
                        await asyncio.sleep(float(response.headers['Retry-After']))
                else:
                    break

        await response.aclose()

        if response.headers.get('content-type', '').lower() == 'application/json':
            data = json.loads(response.content)
        else:
            data = response.content

        if response.status_code >= 400:
            raise RestError(self, method, url, response, data)

        return data

    def close(self):
        return self.client.aclose()
