from .basestate import BaseState
from .. import http
from ..objects.inviteobject import Invite

__all__ = ('InviteState',)


class InviteState(BaseState):
    def upsert(self, data):
        invite = self.get(data['code'])

        if invite is not None:
            invite.update(data)
        else:
            invite = Invite.unmarshal(data, state=self)
            invite.cache()

        return invite

    async def fetch(self, code, *, with_counts=None, with_expiration=None):
        params = {}

        if with_counts is not None:
            params['with_counts'] = with_counts

        if with_expiration is not None:
            params['with_exipration'] = with_expiration

        data = await http.get_invite.request(
            self.client.http, invite_code=code, params=params
        )

        return self.upsert(data)

    async def delete(self, code):
        await http.delete_invite.request(self.client.http, invite_code=code)
