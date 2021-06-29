from datetime import datetime

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils.enum import Enum
from ..utils.json import JsonField, JsonTemplate
from ..utils.snowflake import Snowflake

__all__ = ('IntegrationType', 'IntegrationExpireBehavior',
           'IntegrationAccount', 'IntegrationApplication', 'Integration')


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

    def __init__(self, *, integration):
        self.integration = integration
        self.bot = None

    def update(self, data, *args, **kwargs):
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

    def __init__(self, *, state):
        super().__init__(state=state)
        self.user = None
        self.application = IntegrationApplication.unmarshal(integration=self)

    @property
    def guild(self):
        return self.state.guild

    @property
    def role(self):
        return self.guild.roles.get(self.role_id)

    async def delete(self):
        await rest.delete_guild_integration.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id, integration_id=self.id))

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.client.users.upsert(user)

        application = data.get('application')
        if application is not None:
            self.application.update(application)
