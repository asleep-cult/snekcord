import builtins

from . import undefined

__all__ = ('alist', 'aset', 'aiter', 'anext', 'aenumerate', 'afilter',
           'amap', 'azip', 'asum', 'asorted', 'amin', 'amax',
           'aany', 'aall')


async def alist(obj):
    values = []
    async for value in obj:
        values.append(value)
    return values


async def aset(obj):
    values = set()
    async for value in obj:
        values.add(value)
    return values


aiter = getattr(builtins, 'aiter', None)
if aiter is None:
    def aiter(obj):
        return type(obj).__aiter__(obj)


anext = getattr(builtins, 'anext', None)
if anext is None:
    async def anext(obj, default=undefined):
        try:
            return await type(obj).__anext__(obj)
        except StopAsyncIteration:
            if default is not undefined:
                return default
            raise


async def aenumerate(obj, start=0):
    i = start
    async for value in obj:
        yield i, value
        i += 1


async def afilter(func, obj):
    async for value in obj:
        if func is not None:
            if not func(value):
                continue
        elif not value:
            continue

        yield value


async def amap(func, obj):
    async for value in obj:
        yield func(value)


async def azip(*objs):
    iterators = tuple(aiter(obj) for obj in objs)
    while True:
        values = []
        for i in range(len(iterators)):
            try:
                values.append(await anext(iterators[i]))
            except StopAsyncIteration:
                return
        yield tuple(values)


async def asum(obj, start=0):
    i = start
    async for value in obj:
        i += value
    return i


async def asorted(obj, *args, **kwargs):
    return sorted(await alist(obj), *args, **kwargs)


async def amin(obj, key=None, default=undefined):
    minimun = default
    async for value in obj:
        if key is not None:
            value = key(value)

        if minimun is undefined or value < minimun:
            minimun = value

    if minimun is undefined:
        raise ValueError('amin() arg is an empty async-gen')

    return minimun


async def amax(obj, key=None, default=undefined):
    minimun = default
    async for value in obj:
        if key is not None:
            value = key(value)

        if minimun is undefined or value > minimun:
            minimun = value

    if minimun is undefined:
        raise ValueError('amax() arg is an empty async-gen')

    return minimun


async def aall(obj):
    async for value in obj:
        if not value:
            return False
    return True


async def aany(obj):
    async for value in obj:
        if value:
            return True
    return False
