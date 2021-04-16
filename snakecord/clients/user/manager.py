import enum

from ...connections.shard import Shard
from ...utils.events import EventPusher


class UserClientEvents(enum.Enum):
    pass


class UserClientManager(EventPusher):
    handlers = UserClientEvents

    def __init__(self, *args, **kwargs) -> None:
        self.shard_range = kwargs.pop('shard_range', range(1))
        super().__init__(*args, **kwargs)
        self.shards = {}
        self.token = None

    async def start(self, token: str, *args, **kwargs):
        self.token = token

        for i in self.shard_range:
            self.shards[i] = Shard(self, i)

        for shard in self.shards.values():
            await shard.connect(*args, **kwargs)
