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
    """The base class for all DISPATCH events recieved from Discord's gateway."""

    shard: Shard = attr.ib()
    """The shard that received the event."""

    payload: JSONObject = attr.ib()
    """The payload sent with the event."""

    @property
    def client(self) -> Client:
        """The client the event is attached to."""
        return self.shard.client
