from __future__ import annotations

from typing import TYPE_CHECKING

from .base_state import BaseCachedClientState
from ..events import (
    BaseEvent,
    InviteCreateEvent,
    InviteDeleteEvent,
    InviteEvents,
)
from ..intents import WebSocketIntents
from ..objects import (
    Invite,
    ObjectWrapper,
)

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import Shard

__all__ = ('InviteState',)


class InviteState(BaseCachedClientState):
    @classmethod
    def unwrap_id(self, object) -> str:
        if isinstance(object, str):
            return object

        if isinstance(object, Invite):
            return object.code

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, InviteState):
                return object.id

            raise TypeError('Expected ObjectWrapper created by InviteState')

        raise TypeError('Expected str, Invite, ObjectWrapper or InviteState')

    async def upsert(self, data) -> Invite:
        invite = self.get(data['code'])
        if invite is not None:
            invite.update(data)
        else:
            invite = Invite.unmarshal(data, state=self)

        guild = data.get('guild')
        if guild is not None:
            await invite.update_guild(guild)

        channel = data.get('channel')
        if channel is not None:
            await invite.update_channel(channel)

        target_user = data.get('target_user')
        if target_user is not None:
            await invite.update_target_user(target_user)

        target_application = data.get('target_application')
        if target_application is not None:
            await invite.update_target_application(target_application)

        stage = data.get('stage_instance')
        if stage is not None:
            await invite.update_stage(stage)

        scheduled_event = data.get('guild_scheduled_event')
        if scheduled_event is not None:
            await invite.update_scheduled_event(scheduled_event)

        return invite

    def on_create(self):
        return self.on(InviteEvents.CREATE)

    def on_delete(self):
        return self.on(InviteEvents.DELETE)

    def get_events(self) -> type[InviteEvents]:
        return InviteEvents

    def get_intents(self) -> WebSocketIntents:
        return WebSocketIntents.GUILDS | WebSocketIntents.GUILD_INVITES

    async def process_event(self, event: str, shard: Shard, payload: JSONData) -> BaseEvent:
        event = self.cast_event(event)

        if event is InviteEvents.CREATE:
            invite = await self.upsert(payload)
            return InviteCreateEvent(shard=shard, payload=payload, invite=invite)

        if event is InviteEvents.DELETE:
            invite = self.pop(payload['code'])
            return InviteDeleteEvent(shard=shard, payload=payload, invite=invite)
