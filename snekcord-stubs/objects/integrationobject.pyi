from __future__ import annotations

import typing as t
from datetime import datetime

from .guildobject import Guild
from .roleobject import Role
from .userobject import User
from ..enums import IntegrationExpireBehavior, IntegrationType
from ..states.integrationstate import IntegrationState
from ..utils import JsonField, JsonObject, Snowflake


class IntegrationAccount(JsonObject):
    id: t.ClassVar[JsonField[Snowflake]]
    name: t.ClassVar[JsonField[str]]


class IntegrationApplication(JsonObject):
    name: t.ClassVar[JsonField[str]]
    icon: t.ClassVar[JsonField[str]]
    description: t.ClassVar[JsonField[str]]
    summary: t.ClassVar[JsonField[str]]

    bot: User | None
    integration: Integration

    def __init__(self, *, integration: Integration) -> None: ...


class Integration(JsonObject):
    name: t.ClassVar[JsonField[str]]
    type: t.ClassVar[JsonField[IntegrationType]]
    enabled: t.ClassVar[JsonField[bool]]
    syncing: t.ClassVar[JsonField[bool]]
    role_id: t.ClassVar[JsonField[Snowflake]]
    enable_emoticons: t.ClassVar[JsonField[bool]]
    expire_behavior: t.ClassVar[JsonField[IntegrationExpireBehavior]]
    expire_grace_period: t.ClassVar[JsonField[int]]
    account: t.ClassVar[JsonField[IntegrationAccount]]
    synced_at: t.ClassVar[JsonField[datetime]]
    subscriber_count: t.ClassVar[JsonField[int]]
    revoked: t.ClassVar[JsonField[bool]]

    state: IntegrationState
    user: User | None
    application: IntegrationAccount | None

    def __init__(self, *, state: IntegrationState) -> None: ...

    @property
    def guild(self) -> Guild: ...

    @property
    def role(self) -> Role | None: ...

    async def delete(self) -> None: ...
