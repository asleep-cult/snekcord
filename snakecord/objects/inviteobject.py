from .baseobject import BaseObject
from .. import rest
from ..templates import InviteTemplate


class Invite(BaseObject, template=InviteTemplate):
    __slots__ = ('guild', 'channel', 'inviter', 'target_user',
                 'target_application')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.guild = None
        self.channel = None
        self.inviter = None
        self.target_user = None
        self.target_application = None

    async def delete(self):
        await rest.delete_invite.request(
            session=self._state.manager.rest,
            fmt=dict(invite_code=self.code))

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        self.id = self.code

        guild = getattr(self, '_guild', None)
        if guild is not None:
            self.guild = self._state.manager.guilds.append(guild)
            del self._guild

        channel = getattr(self, '_channel', None)
        if channel is not None:
            self.channel = self._state.manager.channels.append(channel)
            del self._channel

        inviter = getattr(self, '_inviter', None)
        if inviter is not None:
            self.inviter = self._state.manager.users.append(inviter)
            del self._inviter

        target_user = getattr(self, '_target_user', None)
        if target_user is not None:
            self.target_user = self._state.manager.users.append(target_user)
            del self._target_user
