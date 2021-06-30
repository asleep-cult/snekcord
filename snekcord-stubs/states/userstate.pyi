from __future__ import annotations

from .basestate import BaseState
from ..objects.userobject import User
from ..typedefs import SnowflakeConvertible
from ..utils.snowflake import Snowflake

__all__ = ('UserState',)


class UserState(BaseState[Snowflake, User]):
    async def fetch(self, user: SnowflakeConvertible) -> User: ...

    async def fetch_self(self) -> User: ...
