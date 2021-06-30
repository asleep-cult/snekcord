from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..utils.snowflake import Snowflake

__all__ = ('UserState',)


class UserState(BaseState):
    def upsert(self, data):
        user = self.get(Snowflake(data['id']))

        if user is not None:
            user.update(data)
        else:
            user = ClientClasses.User.unmarshal(data, state=self)
            user.cache()

        return user

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_user.request(
            session=self.client.rest,
            fmt=dict(user_id=user_id))

        return self.upsert(data)

    async def fetch_self(self):
        data = await rest.get_user_client.request(
            session=self.client.rest)

        return self.upsert(data)
