from .basestate import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from .. import rest
from ..objects.userobject import User
from ..utils import Snowflake

__all__ = ('UserState',)


class UserState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __user_class__ = User

    def append(self, data):
        user = self.get(data['id'])
        if user is not None:
            user.update(data)
        else:
            user = self.__user_class__.unmarshal(data, state=self)
            user.cache()

        return user

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_user.request(
            session=self.manager.rest,
            fmt=dict(user_id=user_id))

        return self.append(data)
