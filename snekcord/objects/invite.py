from __future__ import annotations

import enum
from datetime import datetime

import attr

from .base import CachedObject, CodeObject
from .. import json
from ..snowflake import Snowflake


class CachedInvite(CachedObject):
    code = json.JSONField('code')
    guild_id = json.JSONField('guild_id')
    channel_id = json.JSONField('channel_id')
    inviter_id = json.JSONField('inviter_id')
    target_type = json.JSONField('target_type')
    target_id = json.JSONField('target_id')
    expires_at = json.JSONField('expires_at')
    uses = json.JSONField('uses')
    max_uses = json.JSONField('max_uses')
    max_age = json.JSONField('max_age')
    temporary = json.JSONField('temporary')
    created_at = json.JSONField('created_at')


class InviteTargetType(enum.IntEnum):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


@attr.s(kw_only=True)
class Invite(CodeObject):
    guild_id: Snowflake = attr.ib()
    channel_id: Snowflake = attr.ib()
    inviter_id: Snowflake = attr.ib()
    target_type: InviteTargetType = attr.ib()
    target_id: Snowflake = attr.ib()
    expires_at: datetime = attr.ib()


@attr.s(kw_only=True)
class RESTInvite(Invite):
    presence_count: int = attr.ib()
    member_count: int = attr.ib()
