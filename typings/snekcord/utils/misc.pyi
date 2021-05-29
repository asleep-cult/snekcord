from typing import (Any, AsyncGenerator, AsyncIterable, Callable,
                    Iterable, Optional, TypeVar, Union,)

T = TypeVar('T')
DT = TypeVar('DT')
RT = TypeVar('RT')


def _validate_keys(name: str, source: Iterable[str],
                   required: Iterable[str], keys: Iterable[str]) -> None: ...


async def alist(obj: AsyncIterable[T]) -> list[T]: ...


async def aset(obj: AsyncIterable[T]) -> set[T]: ...


def aiter(obj: AsyncIterable[T]) -> AsyncIterable[T]: ...


def anext(obj: AsyncIterable[T]) -> T: ...


def aenumerate(obj: AsyncIterable[T], start: int = ...
               ) -> AsyncGenerator[tuple[int, T]]: ...


def afilter(func: Callable[[T], bool], obj: AsyncIterable[T]
            ) -> AsyncGenerator[T]: ...


def amap(func: Callable[[T], RT], obj: AsyncIterable[T]
         ) -> AsyncGenerator[RT]: ...


def azip(*objs: T) -> AsyncGenerator[list[T], None, None]: ...


async def asum(obj: AsyncIterable[T], start: T = ...) -> T: ...


async def asorted(obj: AsyncIterable[T], *,
                  key: Optional[Callable[[T], Any]] = ...) -> Iterable[T]: ...


async def amin(obj: AsyncIterable[T], key: Optional[Callable[[T], Any]],
               default: DT = ...) -> Union[T, DT]: ...


async def amax(obj: AsyncIterable[T], key: Optional[Callable[[T], Any]],
               default: DT = ...) -> Union[T, DT]: ...
