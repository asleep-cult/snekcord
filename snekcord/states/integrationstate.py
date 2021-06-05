from .basestate import BaseState
from .. import rest
from ..objects.integrationobject import Integration
from ..utils import Snowflake


class IntegrationState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __integration_class__ = Integration

    def __init__(self, *, manager, guild):
        super().__init__(manager=manager)
        self.guild = guild

    def upsert(self, data):
        integration = self.get(data['id'])
        if integration is not None:
            integration.update(data)
        else:
            integration = self.__integration_class__.unmarshal(
                data, state=self)
            integration.cache()

        return integration

    async def fetch_all(self):
        data = await rest.get_guild_integrations.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.upsert_many(data)
