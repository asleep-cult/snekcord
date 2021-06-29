from .basestate import BaseState
from ..clients.client import Client
from ..objects.guildobject import Guild
from ..objects.integrationobject import Integration
from ..typedefs import SnowflakeConvertible
from ..utils.snowflake import Snowflake


class IntegrationState(
        BaseState[SnowflakeConvertible, Snowflake, Integration]):
    guild: Guild

    def __init__(self, *, client: Client, guild: Guild) -> None: ...

    async def fetch_all(self) -> set[Integration]: ...
