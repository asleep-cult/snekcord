import typing

from .base_state import CachedEventState
from ..objects import (
    CachedRole,
    Role,
    SnowflakeWrapper,
)
from ..snowflake import Snowflake

__all__ = (
    'SupportsRoleID',
    'RoleIDWrapper',
    'RoleState',
)

SupportsRoleID = typing.Union[Snowflake, str, int, Role]
RoleIDWrapper = SnowflakeWrapper[SupportsRoleID, Role]


class RoleState(CachedEventState[SupportsRoleID, Snowflake, CachedRole, Role]):
    def to_unique(self, object: SupportsRoleID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, Role):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or Role')
