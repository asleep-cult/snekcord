from .connection import Shard


class Gateway:
    def __init__(self, client, *, max_shards, intents=None):
        self._client = client
        self.max_shards = max_shards
        self.intents = intents
        self.shards = {}
        self.multi_sharded = False
        self.recommended_shards = None
        self.url = None
        self.total = None
        self.remaining = None
        self.reset_after = None
        self.max_concurrency = None

    async def connect(self):
        resp = await self._client.rest.get_gateway_bot()
        data = await resp.json()
        self.url = data['url']
        self.recommended_shards = data['shards']
        session_start_limit = data['session_start_limit']
        self.total = session_start_limit['total']
        self.remaining = session_start_limit['total']
        self.reset_after = session_start_limit['reset_after']
        self.max_concurrency = session_start_limit['reset_after']
        if self.remaining == 0:
            raise ConnectionError('This client is out of session starts, please try again in {}'.format(
                self.reset_after))
        shard_range = min((self.recommended_shards, self.max_shards))
        if shard_range > 1:
            self.multi_sharded = True
        for shard_id in range(shard_range):
            shard = Shard(self._client, self.url, shard_id)
            self.shards[shard_id] = shard
        for shard in self.shards.values():
            await shard.connect()
