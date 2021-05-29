from .basestate import BaseState
from .. import rest
from ..objects.inviteobject import Invite

__all__ = ('InviteState',)


class InviteState(BaseState):
    __invite_class__ = Invite

    def upsert(self, data):
        invite = self.get(data['code'])
        if invite is not None:
            invite.update(data)
        else:
            invite = self.__invite_class__.unmarshal(data, state=self)
            invite.cache()

        return invite

    async def fetch(self, code, with_counts=None, with_expiration=None):
        params = {}

        if with_counts is not None:
            params['with_counts'] = with_counts

        if with_expiration is not None:
            params['with_exipration'] = with_expiration

        data = await rest.get_invite.request(
            session=self.manager.rest, fmt=dict(invite_code=code), params=params
        )

        return self.upsert(data)
