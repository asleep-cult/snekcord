import typing as t

from .client import Client
from ..objects.userobject import User
from ..typedefs import Json
from ..utils.bitset import Bitset, Flag
from ..ws.shardws import Shard

__all__ = ('WebSocketIntents', 'WebSocketClient')


class WebSocketIntents(Bitset):
    guilds = Flag(0)
    guild_members = Flag(1)
    guild_bans = Flag(2)
    guild_emojis = Flag(3)
    guild_integrations = Flag(4)
    guild_webhooks = Flag(5)
    guild_invites = Flag(6)
    guild_voice_states = Flag(7)
    guild_presences = Flag(8)
    guild_messages = Flag(9)
    guild_message_reactions = Flag(10)
    guild_message_typing = Flag(11)
    direct_messages = Flag(12)
    direct_message_reactions = Flag(13)
    direct_message_typing = Flag(14)


class WebSocketClient(Client):
    is_user: bool
    intents: WebSocketIntents | None
    timeouts: dict[str, float] | None
    ws_version: str
    shards: dict[int, Shard]

    def __init__(self, *args: t.Any, user: bool = ...,
                 intents: WebSocketIntents | None = ...,
                 timeouts: dict[str, float] | None = ...,
                 ws_version: str = ..., **kwargs) -> None: ...

    @property
    def user(self) -> User | None: ...

    async def fetch_gateway(self) -> Json: ...

    async def fetch_gateway_bot(self) -> Json: ...

    async def connect(self, *args: t.Any, **kwrags: t.Any) -> None: ...

    def run_forever(self) -> BaseException | None: ...
