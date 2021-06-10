from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.inviteobject import Invite

__all__ = ('InviteState',)

if t.TYPE_CHECKING:
    from ..typing import Json


class InviteState(BaseState[str, Invite]):
    __invite_class__ = Invite

    def upsert(self, data: Json) -> Invite:  # type: ignore
        invite = self.get(data['code'])
        if invite is not None:
            invite.update(data)
        else:
            invite = self.__invite_class__.unmarshal(data, state=self)
            invite.cache()

        return invite

    async def fetch(  # type: ignore
        self, code: str, *,
        with_counts: t.Optional[bool] = None,
        with_expiration: t.Optional[bool] = None
    ) -> Invite:
        params: Json = {}

        if with_counts is not None:
            params['with_counts'] = with_counts

        if with_expiration is not None:
            params['with_exipration'] = with_expiration

        data = await rest.get_invite.request(
            session=self.client.rest,
            fmt=dict(invite_code=code),
            params=params)

        return self.upsert(data)
