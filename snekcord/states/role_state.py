from .base_state import BaseState
from ..objects import (
    ObjectWrapper,
    Role,
)
from ..snowflake import Snowflake

__all__ = ('RoleState',)


class RoleState(BaseState):
    def __init__(self, *, client, guild) -> None:
        super().__init__(client=client)
        self.guild = guild

    @classmethod
    def unwrap_id(cls, object):
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (int, str)):
            return Snowflake(object)

        if isinstance(object, Role):
            return object.id

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, cls):
                return object.id

            raise TypeError('Expected ObjectWrapper created by RoleState')

        raise TypeError('Expectes Snowflake, int, str, Role or ObjectWrapper')

    async def upsert(self, data):
        role = self.get(data['id'])
        if role is not None:
            role.update(data)
        else:
            role = Role.unmarshal(data, state=self)

        tags = data.get('tags')
        if tags is not None:
            role._update_tags(tags)

        return role
