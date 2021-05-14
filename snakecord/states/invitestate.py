from .basestate import BaseState
from .. import rest
from ..objects.inviteobject import Invite


class InviteState(BaseState):
    __invite_class__ = Invite

    def append(self, data):
        invite = self.get(data['code'])
        if invite is not None:
            invite.update(data)
        else:
            invite = self.__invite_class__.unmarshal(data)
            invite.cache()

        return invite

    async def fetch(self, code, with_counts=None, with_expiration=None):
        params = {}

        if with_counts is not None:
            params['with_counts'] = with_counts

        if with_expiration is not None:
            params['with_exipration'] = with_expiration

        data = await rest.get_invite.request(
            session=self.manager.rest,
            fmt=dict(invite_code=code),
            params=params)

        return self.append(data)

    async def delete(self, code):
        await rest.delete_invite.request(
            session=self.manager.rest,
            fmt=dict(code=code))
