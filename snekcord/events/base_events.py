from __future__ import annotations

import typing

import attr

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..json import JSONObject
    from ..websockets import Shard

__all__ = ('BaseEvent',)


@attr.s(kw_only=True)
class BaseEvent:
    shard: Shard = attr.ib()
    payload: JSONObject = attr.ib()

    @property
    def client(self) -> Client:
        return self.shard.client
