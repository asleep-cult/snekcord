from __future__ import annotations

import typing as t
from datetime import datetime

from .guildobject import Guild
from .roleobject import Role
from .userobject import User
from ..states.integrationstate import IntegrationState
from ..utils.enum import Enum
from ..utils.json import JsonField, JsonObject
from ..utils.snowflake import Snowflake


class IntegrationType(Enum[str]):
    TWITCH: t.ClassVar[str]
    YOUTUBE: t.ClassVar[str]
    DISCORD: t.ClassVar[str]


class IntegrationExpireBehavior(Enum[int]):
    REMOVE_ROLE: t.ClassVar[int]
    KICK: t.ClassVar[int]


class IntegrationAccount(JsonObject):
    id: JsonField[Snowflake]
    name: JsonField[str]


class IntegrationApplication(JsonObject):
    name: JsonField[str]
    icon: JsonField[str]
    description: JsonField[str]
    summary: JsonField[str]

    bot: User | None
    integration: Integration

    def __init__(self, *, integration: Integration) -> None: ...


class Integration(JsonObject):
    name: JsonField[str]
    type: JsonField[IntegrationType]
    enabled: JsonField[bool]
    syncing: JsonField[bool]
    role_id: JsonField[Snowflake]
    enable_emoticons: JsonField[bool]
    expire_behavior: JsonField[IntegrationExpireBehavior]
    expire_grace_period: JsonField[int]
    account: JsonField[IntegrationAccount]
    synced_at: JsonField[datetime]
    subscriber_count: JsonField[int]
    revoked: JsonField[bool]

    state: IntegrationState
    user: User | None
    application: IntegrationAccount | None

    def __init__(self, *, state: IntegrationState) -> None: ...

    @property
    def guild(self) -> Guild: ...

    @property
    def role(self) -> Role | None: ...

    async def delete(self) -> None: ...
