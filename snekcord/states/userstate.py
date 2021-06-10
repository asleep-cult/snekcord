from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.userobject import User
from ..utils import Snowflake

__all__ = ('UserState',)

if t.TYPE_CHECKING:
    from ..typing import Json, SnowflakeType


class UserState(BaseState[Snowflake, User]):
    __key_transformer__ = Snowflake.try_snowflake
    __user_class__ = User

    def upsert(self, data: Json) -> User:  # type: ignore
        user = self.get(data['id'])
        if user is not None:
            user.update(data)
        else:
            user = self.__user_class__.unmarshal(data, state=self)
            user.cache()

        return user

    async def fetch(self, user: SnowflakeType) -> User:  # type: ignore
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_user.request(
            session=self.client.rest,
            fmt=dict(user_id=user_id))

        return self.upsert(data)

    async def fetch_self(self) -> User:
        data = await rest.get_user_client.request(
            session=self.client.rest)

        return self.upsert(data)
