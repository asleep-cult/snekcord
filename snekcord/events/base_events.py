from __future__ import annotations

import typing

import attr

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..websockets import Shard

__all__ = ('BaseEvent',)

DataT = typing.TypeVar('DataT', bound=typing.Mapping[str, typing.Any])


@attr.s(kw_only=True)
class BaseEvent(typing.Generic[DataT]):
    """The base class for all DISPATCH events recieved from Discord's gateway."""

    shard: Shard = attr.ib()
    """The shard that received the event."""

    data: DataT = attr.ib()
    """The data sent with the event."""

    @property
    def client(self) -> Client:
        """The client the event is attached to."""
        return self.shard.client
