import asyncio
import datetime
from typing import Tuple


class HTTPError(Exception):
    def __init__(self, response) -> None:
        super().__init__()
        self.response = response


class RequestThrottler:
    def __init__(self, endpoint, session) -> None:
        self.endpoint = endpoint
        self.session = session
        self.limit = None
        self.remaining = None
        self.reset = None
        self.reset_after = None
        self.bucket = None
        self.running = False
        self._queue = asyncio.Queue()

    def calculate_reset(self):
        if self.reset is not None:
            return self.reset
        return datetime.now().timestamp() + (self.reset_after / 1000)

    async def _request(self, future, *args, **kwargs) -> None:
        try:
            response = await self.session.request(self.endpoint.method,
                                                  *args, **kwargs)
        except Exception as e:
            self.future.set_exception(e)
            return

        self.limit = response.headers.get('X-RateLimit-Limit')
        self.remaining = response.headers.get('X-RateLimit-Remaining')
        self.reset = response.headers.get('X-RateLimit-Reset')
        self.reset_after = response.headers.get('X-RateLimit-Reset-After')
        self.bucket = response.headers.get('X-RateLimit-Bucket')

        if response.status > 400:
            future.set_exception(HTTPError(response))

        data = await response.data()
        future.set_result(data)


class HTTPEndpoint:
    def __init__(self, method: str, url: str, *,
                 params: Tuple[str] = (),
                 json: Tuple[str] = ()) -> None:
        self.method = method
        self.url = url
        self.params = params
        self.json = json
        self.throttlers = {}

    def throttler_for(self, fmt, session):
        major_params = ('channel_id', 'guild_id', 'webhook_id',
                        'webhook_token')

        key = (session.token
               + '-'.join(fmt.get(key, '') for key in major_params))

        throttler = self.throttlers.get(key)
        if throttler is None:
            throttler = RequestThrottler(self, session)

        return throttler

    def request(self, *, session, fmt={}, params=None, json=None):
        if params is not None:
            params = {k: v for k, v in params.items() if k in self.params}

        if json is not None:
            json = {k: v for k, v in json.items() if k in self.json}

        throttler = self.throttler_for(fmt, session)
        return throttler.submit(self.method, self.url % fmt,
                                params=params, json=json)
