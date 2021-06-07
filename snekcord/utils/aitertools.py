from __future__ import annotations

import builtins
import typing as t

from .undefined import Undefined, undefined

__all__ = ('alist', 'aset', 'aiter', 'anext', 'aenumerate',
           'afilter', 'amap', 'azip', 'asum', 'asorted', 'amin', 'amax',
           'aany', 'aall')

T = t.TypeVar('T')
DT = t.TypeVar('DT')
HT = t.TypeVar('HT', bound=t.Hashable)
RT = t.TypeVar('RT')


async def alist(obj: t.AsyncIterable[T]) -> list[T]:
    values: list[T] = []
    async for value in obj:
        values.append(value)
    return values


async def aset(obj: t.AsyncIterable[HT]) -> set[HT]:
    values: set[HT] = set()
    async for value in obj:
        values.add(value)
    return values


def aiter(obj: t.AsyncIterable[T]) -> t.AsyncIterator[T]:
    return type(obj).__aiter__(obj)


if not t.TYPE_CHECKING and hasattr(builtins, 'aiter'):
    aiter = builtins.aiter


@t.overload
async def anext(obj: t.AsyncIterator[T]) -> T:
    ...


@t.overload
async def anext(obj: t.AsyncIterator[T],
                default: DT | Undefined = undefined) -> T | DT | Undefined:
    ...


async def anext(obj: t.AsyncIterator[T],
                default: DT | Undefined = undefined) -> T | DT | Undefined:
    try:
        return await type(obj).__anext__(obj)
    except StopAsyncIteration:
        if default is not undefined:
            return default
        raise

if not t.TYPE_CHECKING and hasattr(builtins, 'anext'):
    anext = builtins.anext


async def aenumerate(obj: t.AsyncIterable[T],
                     start: int = 0) -> t.AsyncGenerator[tuple[int, T], None]:
    i = start
    async for value in obj:
        yield i, value
        i += 1


async def afilter(func: t.Callable[[T], t.Any] | None,
                  obj: t.AsyncIterable[T]) -> t.AsyncGenerator[T, None]:
    async for value in obj:
        if func is not None:
            if not func(value):
                continue
        elif not value:
            continue

        yield value


async def amap(func: t.Callable[[T], RT],
               obj: t.AsyncIterable[T]) -> t.AsyncGenerator[RT, None]:
    async for value in obj:
        yield func(value)


async def azip(*objs: t.AsyncIterable[t.Any]) -> t.AsyncGenerator[t.Any, None]:
    iterators = tuple(aiter(obj) for obj in objs)
    while True:
        values: list[t.Any] = []
        for i in range(len(iterators)):
            try:
                values.append(await anext(iterators[i]))
            except StopAsyncIteration:
                return
        yield tuple(values)


async def asum(obj: t.AsyncIterable[int], start: int = 0) -> int:
    i = start
    async for value in obj:
        i += value
    return i


async def asorted(obj: t.AsyncIterable[T], *, key: t.Callable[[T], int],
                  reverse: bool = False) -> list[T]:
    return sorted(await alist(obj), key=key, reverse=reverse)


async def amin(obj: t.AsyncIterable[t.Any],
               key: t.Callable[[t.Any], t.Any] | None = None,
               default: t.Any = undefined) -> t.Any:
    minimun = default
    async for value in obj:
        if key is not None:
            value = key(value)

        if minimun is undefined or value < minimun:
            minimun = value

    if minimun is undefined:
        raise ValueError('amin() arg is an empty async-gen')

    return minimun


async def amax(obj: t.AsyncIterable[t.Any],
               key: t.Callable[[t.Any], t.Any] | None = None,
               default: t.Any = undefined) -> t.Any:
    minimun = default
    async for value in obj:
        if key is not None:
            value = key(value)

        if minimun is undefined or value > minimun:
            minimun = value

    if minimun is undefined:
        raise ValueError('amax() arg is an empty async-gen')

    return minimun


async def aall(obj: t.AsyncIterable[t.Any]) -> bool:
    async for value in obj:
        if not value:
            return False
    return True


async def aany(obj: t.AsyncIterable[t.Any]) -> bool:
    async for value in obj:
        if value:
            return True
    return False
