from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..utils import Snowflake

__all__ = ('IntegrationState',)


class IntegrationState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake

    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data):
        integration = self.get(data['id'])
        if integration is not None:
            integration.update(data)
        else:
            integration = ClientClasses.Integration.unmarshal(data, state=self)
            integration.cache()

        return integration

    async def fetch_all(self):
        data = await rest.get_guild_integrations.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.upsert_many(data)
