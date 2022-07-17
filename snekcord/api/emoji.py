import typing

from ..snowflake import Snowflake

if typing.TYPE_CHECKING:
    from .user import RawUser


class RawCustomEmoji(typing.TypedDict):
    id: Snowflake
    name: str
    roles: typing.List[Snowflake]
    user: RawUser
    require_colons: bool
    managed: bool
    animated: bool
    available: bool


class RawStandardEmoji(typing.TypedDict):
    id: None
    name: str
