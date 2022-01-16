from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..clients import Client
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

    @property
    def client(self) -> Client:
        return self.shard.client
