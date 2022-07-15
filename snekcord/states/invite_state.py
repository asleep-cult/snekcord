import typing

from ..events import InviteEvents
from ..objects import CachedInvite, Invite, SupportsInviteCode
from .base_state import CachedEventState

__all__ = ('InviteState',)


class InviteState(CachedEventState[SupportsInviteCode, str, CachedInvite, Invite]):
    @property
    def events(self) -> typing.Tuple[str, ...]:
        return tuple(InviteEvents)

    def to_unique(self, object: SupportsInviteCode) -> str:
        if isinstance(object, str):
            return object

        elif isinstance(object, Invite):
            return object.code

        raise TypeError('Expected str or Invite')
