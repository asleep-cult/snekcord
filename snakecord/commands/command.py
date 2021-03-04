from asyncio import iscoroutine

from .exceptions import InvokeGuardFailure


class InvokeGuard:
    def __init__(self, func):
        self.func = func

    async def __call__(self, *args, **kwargs):
        ret = self.func(*args, **kwargs)
        if iscoroutine(ret):
            ret = await ret
        return ret


class Command:
    def __init__(self, func, *, name=None, description=None, guards=None):
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__
        self.guards = guards or []

    async def call_guards(self, message):
        for guard in self.guards:
            ret = await guard(message)
            if ret is False:
                raise InvokeGuardFailure('InvokeGuard {!r} returned False'.format(guard))

    async def invoke(self, message):
        await self.call_guards(message)
        await self()

    async def __call__(self, message):
        ret = self.func(message)
        if iscoroutine(ret):
            await ret
