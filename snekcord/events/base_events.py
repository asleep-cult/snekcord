from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..clients import Client
    from ..json import JSONObject
    from ..websockets import Shard

__all__ = ('BaseEvent',)


class BaseEvent:
    __slots__ = ('shard', 'payload')

    def __init__(self, *, shard: Shard, payload: JSONObject) -> None:
        self.shard = shard
        self.payload = payload

    @property
    def client(self) -> Client:
        return self.shard.client
