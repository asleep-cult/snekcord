from .basestate import BaseState
from .. import http
from ..objects.userobject import User
from ..snowflake import Snowflake

__all__ = ('UserState',)


class UserState(BaseState):
    def upsert(self, data):
        user = self.get(Snowflake(data['id']))

        if user is not None:
            user.update(data)
        else:
            user = User.unmarshal(data, state=self)
            user.cache()

        return user

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await http.get_user.request(self.client.http, user_id=user_id)

        return self.upsert(data)

    async def fetch_me(self):
        data = await http.get_me.request(self.client.http)

        return self.upsert(data)
