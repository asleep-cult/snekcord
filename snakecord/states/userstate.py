from .basestate import BaseState
from .. import rest
from ..objects.userobject import User
from ..utils import Snowflake

__all__ = ('UserState',)


class UserState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __user_class__ = User

    def new(self, data):
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

        return self.new(data)
