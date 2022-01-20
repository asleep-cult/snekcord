from __future__ import annotations

import enum
from datetime import datetime

from .base import CodeObject
from .. import json
from ..collection import Collection

__all__ = ('InviteTargetType', 'InviteStage', 'Invite')


class InviteTargetType(enum.IntEnum):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


class InviteStage(json.JSONObject):
    __slots__ = ('invite', 'members')

    participant_count = json.JSONField('participant_count')
    speaker_count = json.JSONField('speaker_count')
    topic = json.JSONField('topic')

    def __init__(self, *, invite: Invite) -> None:
        self.invite = invite
        self.members = Collection()

    async def update_members(self, members) -> None:
        assert self.invite.guild is not None
        self.members.clear()

        for member in members:
            member = await self.invite.guild.members.upsert(member)
            self.members[member.id] = member


class Invite(CodeObject):
    __slots__ = (
        'guild',
        'channel',
        'target_user',
        'target_application',
        'stage',
        'scheduled_event',
    )

    target_type = json.JSONField('target_type', InviteTargetType)
    presence_count = json.JSONField('approximate_presence_count')
    member_count = json.JSONField('approximate_member_count')
    expires_at = json.JSONField('expires_at', datetime.fromisoformat)

    def __init__(self, *, state) -> None:
        super().__init__(state=state)

        self.guild = None
        self.channel = None
        self.target_user = None
        self.target_application = None
        self.stage = None
        self.scheduled_event = None

    async def update_guild(self, data) -> None:
        self.guild = await self.client.guilds.upsert(data)

    async def update_channel(self, data) -> None:
        self.channel = await self.client.channels.upsert(data)

    async def update_target_user(self, data) -> None:
        self.target_user = await self.client.users.upsert(data)

    async def update_target_application(self, data) -> None:
        self.application = await self.client.applications.upsert(data)

    async def update_stage(self, data) -> None:
        if self.stage is None:
            self.stage = InviteStage.unmarshal(data, invite=self)
        else:
            self.stage.update(data)

        members = data.get('members')
        if members is not None:
            await self.stage.update_members(members)

    async def update_scheduled_event(self, data) -> None:
        self.scheduled_event = await self.client.scheduled_events.upsert(data)
