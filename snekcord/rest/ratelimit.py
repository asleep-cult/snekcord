import asyncio
from datetime import datetime, timedelta

MAJOR_PARAMS = ('channel_id', 'guild_id', 'webhook_id', 'webhook_token')


class RatelimitBucket:
    def __init__(self, bucket):
        self.bucket = bucket
        self.limit = None
        self.remaining = None
        self.reset = None
        self.lock = asyncio.Lock()

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} lock={self.lock!r},'
            f' limit={self.limit}, remaining={self.remaining}, reset={self.reset}>'
        )

    async def __aenter__(self):
        await self.lock.acquire()

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        if self.remaining == 0:
            if self.reset is not None:
                await asyncio.sleep((self.reset - datetime.utcnow()).total_seconds())
                self.reset = None

        self.lock.release()

    @classmethod
    def from_request(cls, cache, method, url, keywords):
        major_params = ':'.join(str(keywords.get(param)) for param in MAJOR_PARAMS)
        bucket = '-'.join((method, url, major_params))

        if bucket in cache:
            return cache[bucket]
        else:
            self = cls(bucket)
            cache[bucket] = self
            return self

    def update(self, response):
        limit = response.headers.get('X-RateLimit-Limit')

        if limit is not None:
            self.limit = int(limit)
        else:
            self.limit = float('inf')

        remaining = response.headers.get('X-RateLimit-Remaining')

        if remaining is not None:
            self.remaining = int(remaining)

        reset = response.headers.get('X-RateLimit-Reset')

        if reset is not None:
            self.reset = datetime.utcfromtimestamp(float(reset))
        else:
            reset_after = response.headers.get('X-RateLimit-Reset-After')

            if reset_after is not None:
                self.reset = datetime.utcnow() + timedelta(seconds=float(reset_after))
