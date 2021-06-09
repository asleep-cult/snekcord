from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import Enum, JsonField, JsonTemplate, Snowflake

__all__ = ('IntegrationAccount', 'IntegrationApplicationTemplate',
           'IntegrationTemplate')

if t.TYPE_CHECKING:
    from .guildobject import Guild
    from .roleobject import Role
    from .userobject import User
    from ..states import IntegrationState
    from ..typing import Json


class IntegrationType(Enum[str]):
    TWITCH = 'twitch'
    YOUTUBE = 'youtube'
    DISCORD = 'discord'


class IntegrationExpireBehavior(Enum[int]):
    REMOVE_ROLE = 0
    KICK = 1


IntegrationAccountTemplate = JsonTemplate(
    name=JsonField('name'),
    __extends__=(BaseTemplate,)
)


class IntegrationAccount(BaseObject, template=IntegrationAccountTemplate):
    name: str


IntegrationApplicationTemplate = JsonTemplate(
    name=JsonField('name'),
    icon=JsonField('icon'),
    description=JsonField('description'),
    summary=JsonField('summary'),
    __extends__=(BaseTemplate,)
)


class IntegrationApplication(BaseObject,
                             template=IntegrationApplicationTemplate):
    __slots__ = ('integration', 'bot')

    if t.TYPE_CHECKING:
        integration: Integration
        bot: t.Optional[User]
        name: str
        icon: t.Optional[str]
        description: str
        summary: str

    def __init__(self, *, integration: Integration) -> None:
        self.integration = integration
        self.bot = None

    def update(  # type: ignore
        self, data: Json, *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        bot = data.get('bot')
        if bot is not None:
            self.bot = self.integration.state.client.users.upsert(bot)


IntegrationTemplate = JsonTemplate(
    name=JsonField('name'),
    type=JsonField(
        'type',
        IntegrationType.get_enum,
        IntegrationType.get_value
    ),
    enabled=JsonField('enabled'),
    syncing=JsonField('syncing'),
    role_id=JsonField('role_id', Snowflake, str),
    enable_emoticons=JsonField('emoticons'),
    expire_behavior=JsonField(
        'expire_behavior',
        IntegrationExpireBehavior.get_enum,
        IntegrationExpireBehavior.get_value
    ),
    expire_grace_period=JsonField('expire_grace_period'),
    account=JsonField('account', object=IntegrationAccount),
    synced_at=JsonField(
        'synced_at',
        datetime.fromisoformat,
        datetime.isoformat
    ),
    subscriber_count=JsonField('subscriber_count'),
    revoked=JsonField('revoked'),
    __extends__=(BaseTemplate,)
)


class Integration(BaseObject, template=IntegrationTemplate):
    __slots__ = ('user', 'application')

    if t.TYPE_CHECKING:
        user: t.Optional[User]
        application: IntegrationApplication
        state: IntegrationState
        name: str
        type: IntegrationType
        enabled: bool
        syncing: t.Optional[bool]
        role_id: t.Optional[Snowflake]
        enable_emoticons: t.Optional[bool]
        expire_behavior: t.Optional[IntegrationExpireBehavior]
        expire_grace_period: int
        account: IntegrationAccount
        synced_at: t.Optional[datetime]
        subscriber_count: t.Optional[int]
        revoked: t.Optional[bool]

    def __init__(self, *, state: IntegrationState):
        super().__init__(state=state)
        self.user = None
        self.application = IntegrationApplication.unmarshal(integration=self)

    @property
    def guild(self) -> Guild:
        return self.state.guild

    @property
    def role(self) -> t.Optional[Role]:
        if self.role_id is not None:
            return self.guild.roles.get(self.role_id)
        return None

    async def delete(self) -> None:
        await rest.delete_guild_integration.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id, integration_id=self.id))

    def update(  # type: ignore
        self, data: Json, *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.client.users.upsert(user)

        application = data.get('application')
        if application is not None:
            self.application.update(application)
