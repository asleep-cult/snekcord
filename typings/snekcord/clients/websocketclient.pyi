from typing import Any, Dict, NamedTuple, Optional, Union
from ..objects.channelobject import DMChannel, GuildChannel

_Channel = Union[DMChannel, GuildChannel]


class ChannnelCreateEvent(NamedTuple):
    shard: Any
    payload: Dict[str, Any]
    channel: _Channel


class ChannelUpdateEvent(NamedTuple):
    ...
