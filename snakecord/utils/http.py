import asyncio
import datetime
from typing import Tuple


class HTTPError(Exception):
    def __init__(self, response, data) -> None:
        super().__init__()
        self.response = response
        self.data = data


class RequestThrottler:
    def __init__(self, endpoint, session) -> None:
        self.endpoint = endpoint
        self.session = session
        self.limit = None
        self.remaining = None
        self.endpoint_resets_after = None
        self.reset_after = None
        self.bucket = None
        self._made_initial_request = False
        self._running = False
        self._lock = asyncio.Lock()
        self._queue = asyncio.Queue()

    def calculate_ratelimit(self, reset, reset_after):
        if reset_after is not None:
            self.reset_after = reset_after
        elif reset is not None:
            self.reset_after = (reset * 1000) - datetime.now().timestamp()

        if self.limit == self.remaining + 1:
            self._made_initial_request = True
            self.endpoint_resets_after = self.reset_after

    async def _request(self, future, *args, **kwargs) -> None:
        try:
            response = await self.session.request(self.endpoint.method,
                                                  *args, **kwargs)
        except Exception as e:
            future.set_exception(e)
            return

        limit = response.headers.get('X-RateLimit-Limit')
        if limit is not None:
            self.limit = int(limit)

        remaining = response.headers.get('X-RateLimit-Remaining')
        if remaining is not None:
            self.remaining = int(remaining)

        reset = response.headers.get('X-RateLimit-Reset')
        if reset is not None:
            reset = float(reset)

        reset_after = response.headers.get('X-RateLimit-Reset-After')
        if reset_after is not None:
            reset_after = float(reset_after)

        self.calculate_ratelimit(reset, reset_after)

        bucket = response.headers.get('X-RateLimit-Bucket')
        if bucket is not None:
            self.bucket = bucket

        data = await response.read()

        if response.status > 400:
            future.set_exception(HTTPError(response, data))
            return

        future.set_result(data)

    async def _do_requests(self):
        self._running = True
        async with self._lock:
            while True:
                await asyncio.sleep(0)

                future, args, kwargs = await self._queue.get()

                if not self._made_initial_request:
                    await self._request(future, *args, **kwargs)

                    if self.remaining == 0:
                        await asyncio.sleep(self.reset_after)
                else:
                    self.session.loop.create_task(
                        self._request(future, *args, **kwargs))

                    self.remaining -= 1
                    if self.remaining == 0:
                        print('SLEEPING FOR ', self.endpoint_resets_after)
                        await asyncio.sleep(self.endpoint_resets_after)
                        self.remaining = self.limit

    def submit(self, *args, **kwargs):
        future = self.session.loop.create_future()
        self._queue.put_nowait((future, args, kwargs))

        if not self._running:
            self.session.loop.create_task(self._do_requests())

        return future


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
               + '-'.join(str(fmt.get(key, '')) for key in major_params))

        throttler = self.throttlers.get(key)
        if throttler is None:
            throttler = RequestThrottler(self, session)
            self.throttlers[key] = throttler

        return throttler

    def request(self, *, session, fmt={}, params=None, json=None):
        if params is not None:
            params = {k: v for k, v in params.items() if k in self.params}

        if json is not None:
            json = {k: v for k, v in json.items() if k in self.json}

        throttler = self.throttler_for(fmt, session)
        return throttler.submit(self.url % fmt,
                                params=params, json=json)
