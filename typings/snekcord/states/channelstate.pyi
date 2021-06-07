from typing import Any, ClassVar, Dict, List, Literal, SupportsInt, Type, Union

from .basestate import BaseState, BaseSubState
from ..objects.baseobject import BaseObject
from ..objects.channelobject import (
    ChannelType, DMChannel, GuildChannel, VoiceChannel
)
from ..objects.guildobject import Guild
from ..utils import Snowflake

_Channel = Union[DMChannel, GuildChannel]
_ConvertableToInt = Union[str, SupportsInt]
_SnowflakeType = Union[_ConvertableToInt, BaseObject[Snowflake]]

class ChannelState(BaseState[Snowflake]):
    __channel_classes__: ClassVar[Dict[ChannelType, Type[_Channel]]]
    __default_class__: Type[BaseObject[Any]]

    def get_class(self, type: type) -> Union[_Channel, BaseObject[Snowflake]]: ...
    def upsert(self, data: Dict[str, Any]) -> _Channel: ...
    async def fetch(
        self, channel: Union[_ConvertableToInt, BaseObject[Snowflake]]
    ) -> _Channel: ...

class GuildChannelState(BaseSubState[Snowflake]):
    guild: Guild
    def __init__(self, *, superstate: ChannelType, guild: Guild) -> None: ...

    @property
    def afk(self) -> VoiceChannel: ...
    @property
    def widget(self) -> GuildChannel: ...
    @property
    def application(self) -> GuildChannel: ...
    @property
    def system(self) -> GuildChannel: ...
    @property
    def rules(self) -> GuildChannel: ...
    @property
    def public_updates(self) -> GuildChannel: ...
    async def fetch_all(self) -> List[GuildChannel]: ...
    async def create(self, name: str, **kwargs: Any) -> GuildChannel: ...
    async def modify_many(
        self, positions: Dict[_SnowflakeType, Dict[Literal['parent'], _SnowflakeType]]
    ) -> None: ...
