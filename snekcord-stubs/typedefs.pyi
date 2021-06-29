import asyncio
import typing as t

from typing_extensions import ParamSpec

from .objects.baseobject import BaseObject
from .objects.channelobject import DMChannel, GuildChannel
from .utils.snowflake import Snowflake

T = t.TypeVar('T')
P = ParamSpec('P')


class SupportsTrunc(t.Protocol):
    def __trunc__(self) -> int: ...


Channel = t.Union[DMChannel, GuildChannel]

IntConvertible = t.Union[str, bytes, t.SupportsInt, t.SupportsIndex,
                         SupportsTrunc]
SnowflakeConvertible = t.Union[IntConvertible, BaseObject[Snowflake]]

AnyCallable = t.Callable[..., t.Any]
Coroutine = t.Coroutine[t.Optional[asyncio.Future[t.Any]], None, T]
CoroCallable = t.Callable[P, Coroutine[T]]
AnyCoroCallable = t.Callable[..., Coroutine[t.Any]]

Json = dict[str, t.Any]
