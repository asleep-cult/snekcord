from .basestate import BaseState
from ..objects.inviteobject import Invite

__all__ = ('InviteState',)


class InviteState(BaseState[str, str, Invite]):
    async def fetch(self, code: str, with_counts: bool | None = ...,
                    with_expiration: bool | None = ...) -> Invite: ...
