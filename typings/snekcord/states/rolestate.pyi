from typing import Any, ClassVar, SupportsInt, Type, Union

from .basestate import BaseState
from ..client import Baseclient
from ..objects.guildobject import Guild
from ..objects.roleobject import Role
from ..utils import Snowflake

_ConvertableToInt = Union[SupportsInt, str]

class RoleState(BaseState[Snowflake]):
    __role_class__: ClassVar[Type[Role]]
    guild: Guild

    def __init__(self, *, client: Baseclient, guild: Guild) -> None: ...
    def upsert(self, data: dict[str, Any]) -> Role: ...
    async def fetch_all(self) -> list[Role]: ...
    async def create(self, **kwargs: Any) -> Role: ...
    async def modify_many(self, positions: dict[Union[_ConvertableToInt, Role], int]) -> None: ...
