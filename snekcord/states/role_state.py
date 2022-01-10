from .base_state import BaseSate
from ..exceptions import UnknownObjectError
from ..objects import (
    ObjectWrapper,
    Role,
)
from ..snowflake import Snowflake

__all__ = ('RoleState',)


class RoleState(BaseSate):
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
        try:
            role = self.get(data['id'])
        except UnknownObjectError:
            role = Role.unmarshal(data, state=self)
        else:
            role.update(data)

        tags = data.get('tags')
        if tags is not None:
            role._update_tags(tags)

        return role
