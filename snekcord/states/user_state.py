from .base_state import BaseSate
from ..exceptions import UnknownObjectError
from ..objects import (
    ObjectWrapper,
    User,
)
from ..rest.endpoints import (
    GET_USER,
)
from ..snowflake import Snowflake

__all__ = ('UserState',)


class UserState(BaseSate):
    @classmethod
    def unwrap_id(cls, object) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (int, str)):
            return Snowflake(object)

        if isinstance(object, User):
            return object.id

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, cls):
                return object.id

            raise TypeError('Expected ObjectWrapper created by UserState')

        raise TypeError('Expected Snowflake, int, str, User or ObjectWrapper')

    async def upsert(self, data):
        try:
            user = self.get(data['id'])
        except UnknownObjectError:
            user = User.unmarshal(data, state=self)
        else:
            user.update(data)

        return user

    async def fetch(self, user):
        user_id = self.unwrap_id(user)

        data = await self.client.request(GET_USER, user_id=user_id)
        assert isinstance(data, dict)

        return await self.upsert(data)
