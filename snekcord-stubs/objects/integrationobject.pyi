from __future__ import annotations

from datetime import datetime

from .guildobject import Guild
from .roleobject import Role
from .userobject import User
from ..states.integrationstate import IntegrationState
from ..utils.enum import Enum
from ..utils.json import JsonObject, JsonTemplate
from ..utils.snowflake import Snowflake


class IntegrationType(Enum[str]):
    TWITCH = 'twitch'
    YOUTUBE = 'youtube'
    DISCORD = 'discord'


class IntegrationExpireBehavior(Enum[int]):
    REMOVE_ROLE = 0
    KICK = 1


IntegrationAccountTemplate: JsonTemplate = ...


class IntegrationAccount(JsonObject, template=IntegrationAccountTemplate):
    name: str


IntegrationApplicationTemplate: JsonTemplate = ...


class IntegrationApplication(JsonObject,
                             template=IntegrationApplicationTemplate):
    name: str
    icon: str
    description: str
    summary: str

    bot: User | None
    integration: Integration

    def __init__(self, *, integration: Integration) -> None: ...


IntegrationTemplate: JsonTemplate = ...


class Integration(JsonObject, template=IntegrationTemplate):
    name: str
    type: IntegrationType
    enabled: bool
    syncing: bool
    role_id: Snowflake
    enable_emoticons: bool
    expire_behavior: IntegrationExpireBehavior
    expire_grace_period: int
    account: IntegrationAccount
    synced_at: datetime
    subscriber_count: int
    revoked: bool

    state: IntegrationState
    user: User | None
    application: IntegrationAccount | None

    def __init__(self, *, state: IntegrationState) -> None: ...

    @property
    def guild(self) -> Guild: ...

    @property
    def role(self) -> Role | None: ...

    async def delete(self) -> None: ...
