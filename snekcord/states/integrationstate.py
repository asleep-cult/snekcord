from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.integrationobject import Integration
from ..utils import Snowflake

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Guild
    from ..typing import Json


class IntegrationState(BaseState[Snowflake, Integration]):
    __key_transformer__ = Snowflake.try_snowflake
    __integration_class__ = Integration

    if t.TYPE_CHECKING:
        guild: Guild

    def __init__(self, *, client: Client, guild: Guild) -> None:
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data: Json) -> Integration:  # type: ignore
        integration = self.get(data['id'])
        if integration is not None:
            integration.update(data)
        else:
            integration = self.__integration_class__.unmarshal(
                data, state=self)
            integration.cache()

        return integration

    async def fetch_all(self) -> t.Set[Integration]:
        data = await rest.get_guild_integrations.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.upsert_many(data)
