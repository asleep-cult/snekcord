import typing

from ..objects import Role, SnowflakeWrapper
from ..snowflake import Snowflake

SupportsRoleID = typing.Union[Snowflake, str, int, Role]
RoleIDWrapper = SnowflakeWrapper[SupportsRoleID, Role]

__all__ = ('SupportsRoleID', 'RoleIDWrapper')
