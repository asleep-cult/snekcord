from .bases import BaseObject, BaseState
from .utils import JsonField, Snowflake, JSON

from typing import Optional


class GuildIntegrationAccount(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
    }

    id: Snowflake
    name: str


class GuildIntegrationApplication(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'icon': JsonField('icon'),
        'description': JsonField('description'),
        'summary': JsonField('summary'),
        '_bot': JsonField('bot'),
    }

    id: Snowflake
    name: str
    icon: Optional[str]
    description: str
    summary: str
    _bot: Optional[JSON]

    def __init__(self, state):
        self._state = state

        if self._bot is not None:
            self.bot = self._state._client.users.add(self._bot)


class GuildIntegration(BaseObject):
    __json_fields__ = {
        'name':  JsonField('name'),
        'type': JsonField('type'),
        'enabled': JsonField('enabled'),
        'syncing': JsonField('syncing'),
        'role_id': JsonField('role_id', Snowflake, str),
        'enable_emoticons': JsonField('enable_emoticons'),
        'expire_behavior': JsonField('expire_behavior'),
        'expire_grace_period': JsonField('expire_grace_period'),
        '_user': JsonField('user'),
        'account': JsonField('account', struct=GuildIntegrationAccount),
        'synced_at': JsonField('synced_at'),
        'subscriber_count': JsonField('subscriber_count'),
        'revoked': JsonField('revoked'),
        '_application': JsonField('application'),
    }

    id: Snowflake
    name: str
    type: int
    enabled: bool
    syncing: Optional[bool]
    role_id: Optional[Snowflake]
    enable_emoticons: Optional[bool]
    expire_behavior: Optional[bool]
    expire_grace_period: Optional[int]
    _user: Optional[JSON]
    account: GuildIntegrationAccount
    synced_at: Optional[str]
    subscriber_count: Optional[int]
    revoked: Optional[bool]
    _application: JSON

    def __init__(self, state, guild):
        self._state = state
        self.guild = guild

    async def edit(
        self,
        *,
        expire_behavior=None,
        expire_grace_period=None,
        enable_emoticons=None
    ):
        rest = self._state._client.rest
        await rest.modify_guild_integration(
            self.guild.id, self.id, expire_behavior=expire_behavior,
            expire_grace_period=expire_grace_period,
            enable_emoticons=enable_emoticons
        )

    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_guild_integration(self.guild.id, self.id)

    async def sync(self):
        rest = self._state._client.rest
        await rest.delete_guild_integration(self.guild.id, self.id)

    def _update(self, *args, **kwargs):
        if self._user is not None:
            self.user = self._state._client.users._add(self._user)

        if self._application is not None:
            self.application = GuildIntegrationApplication.unmarshal(
                self._application,
                state=self._state
            )


class GuildIntegrationState(BaseState):
    __state_class__ = GuildIntegration

    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data):
        integration = self.get(data['id'])
        if integration is not None:
            integration._update(data, set_default=False)
            return integration
        integration = self.__state_class__.unmarshal(
            data,
            state=self,
            guild=self._guild
        )
        self._values[integration.id] = integration
        return integration

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_guild_integrations(self._guild.id)
        data = await resp.json()
        integrations = []
        for integration in data:
            integration = self._add(integration)
            integrations.append(integration)
        return integrations

    async def create(self, integration_id, integration_type):
        rest = self._client.rest
        await rest.create_guild_integration(integration_type, integration_id)
