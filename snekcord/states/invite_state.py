import typing

from ..events import InviteEvents
from ..objects import CachedInvite, CodeWrapper, Invite
from .base_state import CachedEventState

__all__ = (
    'SupportsInviteCode',
    'InviteCodeWrapper',
    'InviteState',
)

SupportsInviteCode = typing.Union[str, Invite]
InviteCodeWrapper = CodeWrapper[SupportsInviteCode, Invite]


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
