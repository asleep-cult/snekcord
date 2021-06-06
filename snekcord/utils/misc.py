import builtins
from typing import (
    Any, AsyncIterable, AsyncIterator, Callable, Generator, Hashable, Iterable,
    List, Optional, Set, Tuple, TypeVar, Union, overload)

from .undefined import undefined

__all__ = ('_validate_keys', 'alist', 'aset', 'aiter', 'anext', 'aenumerate',
           'afilter', 'amap', 'azip', 'asum', 'asorted', 'amin', 'amax',
           'aany', 'aall')

T = TypeVar('T')
DT = TypeVar('DT')
HT = TypeVar('HT', bound=Hashable)
RT = TypeVar('RT')


def _validate_keys(name: str, source: Iterable[str], required: Iterable[str], keys: Iterable[str]):
    for key in required:
        if key not in source:
            raise ValueError(f'{name} is missing required key {key!r}')

    for key in source:
        if key not in keys:
            raise ValueError(f'{name} received an unexpected key {key!r}')


async def alist(obj: AsyncIterable[T]) -> List[T]:
    values: List[T] = []
    async for value in obj:
        values.append(value)
    return values


async def aset(obj: AsyncIterable[HT]) -> Set[HT]:
    values: Set[HT] = set()
    async for value in obj:
        values.add(value)
    return values


aiter: Callable[[AsyncIterable[T]], AsyncIterable[T]] = getattr(builtins, 'aiter', None)  # type: ignore

if aiter is None:
    def aiter(obj: AsyncIterable[T]) -> AsyncIterable[T]:
        return type(obj).__aiter__(obj)


anext: Callable[[AsyncIterator[T]], T] = getattr(builtins, 'anext', None)  # type: ignore

if anext is None:
    @overload
    async def anext(obj: AsyncIterator[T]) -> T:
        ...

    @overload
    async def anext(obj: AsyncIterator[T], default: DT) -> Union[T, DT]:
        ...

    async def anext(obj: AsyncIterator[Any], default: Any = undefined) -> Any:
        try:
            return await type(obj).__anext__(obj)
        except StopAsyncIteration:
            if default is not undefined:
                return default
            raise


async def aenumerate(obj: AsyncIterable[T], start: int = 0
) -> Generator[Tuple[int, T], None, None]:
    i = start
    async for value in obj:
        yield i, value
        i += 1


async def afilter(func: Optional[Callable[[T], Any]], obj: T
) -> Generator[T, None, None]:
    async for value in obj:
        if value or func is not None and func(value):
            yield value


async def amap(func: Callable[[T], RT], obj: T
) -> Generator[RT, None, None]:
    async for value in obj:
        yield func(value)


async def azip(*objs: T) -> Generator[Tuple[T, ...], None, None]:
    iterators = tuple(aiter(obj) for obj in objs)
    while True:
        values = []
        for i in range(len(iterators)):
            try:
                values.append(await anext(iterators[i]))
            except StopAsyncIteration:
                return
        yield tuple(values)


async def asum(obj: AsyncIterable[T], start: T = 0) -> T:
    i = start
    async for value in obj:
        i += value
    return i


async def asorted(
    obj, *, key: Optional[Callable[[T], Any]], reverse: bool = False
) -> List[T]:
    return sorted(await alist(obj), key=key, reverse=reverse)


@overload
async def amin(obj: AsyncIterable[T], key: Callable[[T], Any] = ...) -> T:
    ...

@overload
async def amin(obj: AsyncIterable[T], key: Optional[Callable[[T], Any]], default: DT
) -> Union[T, DT]: ...

async def amin(obj: AsyncIterable[T], key: Optional[Callable[[T], Any]] = None, default: DT = undefined
) -> Union[T, DT]:
    minimun = default
    async for value in obj:
        if key is not None:
            value = key(value)

        if minimun is undefined or value < minimun:
            minimun = value

    if minimun is undefined:
        raise ValueError('amin() arg is an empty async-gen')

    return minimun


@overload
async def amax(obj: AsyncIterable[T], *, key: Callable[[T], Any] = ...) -> T:
    ...

@overload
async def amax(obj: AsyncIterable[T], *, key: Optional[Callable[[T], Any]] = ..., default: DT,
) -> Union[T, DT]: ...

async def amax(obj: AsyncIterable[T], key: Optional[Callable[[T], Any]] = None, default: DT = undefined
) -> Union[T, DT]:
    minimun = default
    async for value in obj:
        if key is not None:
            value = key(value)

        if minimun is undefined or value > minimun:
            minimun = value

    if minimun is undefined:
        raise ValueError('amax() arg is an empty async-gen')

    return minimun


async def aall(obj: AsyncIterable[Any]) -> bool:
    async for value in obj:
        if not value:
            return False
    return True


async def aany(obj: AsyncIterable[Any]) -> bool:
    async for value in obj:
        if value:
            return True
    return False
