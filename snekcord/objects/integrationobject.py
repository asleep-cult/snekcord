from datetime import datetime

from .baseobject import BaseObject
from ..enums import IntegrationExpireBehavior, IntegrationType
from ..utils import JsonField, JsonObject, Snowflake

__all__ = ('IntegrationAccount', 'IntegrationApplication', 'Integration')


class IntegrationAccount(JsonObject):
    id = JsonField('id', Snowflake)
    name = JsonField('name')


class IntegrationApplication(JsonObject):
    __slots__ = ('integration', 'bot')

    name = JsonField('name')
    icon = JsonField('icon')
    description = JsonField('description')
    summary = JsonField('summary')

    def __init__(self, *, integration):
        self.integration = integration
        self.bot = None

    def update(self, data):
        super().update(data)

        if 'bot' in data:
            self.bot = self.integration.state.client.users.upsert(data['bot'])

        return self


class Integration(BaseObject):
    __slots__ = ('user', 'application')

    name = JsonField('name')
    type = JsonField('type', IntegrationType.get_enum)
    enabled = JsonField('enabled')
    syncing = JsonField('syncing')
    role_id = JsonField('role_id', Snowflake)
    enable_emoticons = JsonField('emoticons')
    expire_behavior = JsonField('expire_behavior', IntegrationExpireBehavior.get_enum)
    expire_grace_period = JsonField('expire_grace_period')
    account = JsonField('account', object=IntegrationAccount)
    synced_at = JsonField('synced_at', datetime.fromisoformat)
    subscriber_count = JsonField('subscriber_count')
    revoked = JsonField('revoked')

    def __init__(self, *, state):
        super().__init__(state=state)

        self.user = None

        self.application = IntegrationApplication(integration=self)

    @property
    def guild(self):
        return self.state.guild

    @property
    def role(self):
        return self.guild.roles.get(self.role_id)

    def delete(self):
        return self.state.delete(self.id)

    def update(self, data):
        super().update(data)

        if 'user' in data:
            self.user = self.state.client.users.upsert(data['user'])

        if 'application' in data:
            self.application.update(data['application'])

        return self
