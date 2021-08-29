from .basestate import BaseState
from .. import http
from ..objects.integrationobject import Integration
from ..snowflake import Snowflake

__all__ = ('IntegrationState',)


class IntegrationState(BaseState):
    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data):
        integration = self.get(Snowflake(data['id']))

        if integration is not None:
            integration.update(data)
        else:
            integration = Integration.unmarshal(data, state=self)
            integration.cache()

        return integration

    async def fetch_all(self):
        data = await http.get_guild_integrations.request(
            self.client.http, guild_id=self.guild.id
        )

        return [self.upsert(guild) for guild in data]

    async def delete(self, integration):
        integration_id = Snowflake.try_snowflake(integration)

        await http.delete_guild_integration.request(
            self.client.http, guild_id=self.guild.id, integration_id=integration_id
        )
