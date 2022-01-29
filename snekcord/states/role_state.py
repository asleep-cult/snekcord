import typing

from ..objects import Role, SnowflakeWrapper
from ..snowflake import Snowflake

__all__ = ('SupportsRoleID', 'RoleIDWrapper')

SupportsRoleID = typing.Union[Snowflake, str, int, Role]
RoleIDWrapper = SnowflakeWrapper[SupportsRoleID, Role]
