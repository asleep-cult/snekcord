from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses

__all__ = ('InviteState',)


class InviteState(BaseState):
    def upsert(self, data):
        invite = self.get(data['code'])

        if invite is not None:
            invite.update(data)
        else:
            invite = ClientClasses.Invite.unmarshal(data, state=self)
            invite.cache()

        return invite

    async def fetch(self, code, *, with_counts=None, with_expiration=None):
        params = {}

        if with_counts is not None:
            params['with_counts'] = with_counts

        if with_expiration is not None:
            params['with_exipration'] = with_expiration

        data = await rest.get_invite.request(
            self.client.rest, invite_code=code, params=params
        )

        return self.upsert(data)

    async def delete(self, code):
        await rest.delete_invite.request(
            self.client.rest, invite_code=code
        )
