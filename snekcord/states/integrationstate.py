from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
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
            integration = ClientClasses.Integration.unmarshal(data, state=self)
            integration.cache()

        return integration

    async def fetch_all(self):
        data = await rest.get_guild_integrations.request(
            self.client.rest, {'guild_id': self.guild.id}
        )

        return [self.upsert(guild) for guild in data]

    async def delete(self, integration):
        integration_id = Snowflake.try_snowflake(integration)

        await rest.delete_guild_integration.request(
            self.client.rest, guild_id=self.guild.id, integration_id=integration_id
        )
