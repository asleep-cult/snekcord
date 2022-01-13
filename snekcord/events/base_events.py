from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import ShardWebSocket

__all__ = ('BaseEvent',)


class BaseEvent:
    __slots__ = ('shard', 'payload')

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData) -> None:
        self.shard = shard
        self.payload = payload

    @staticmethod
    def get_type():
        raise NotImplementedError
