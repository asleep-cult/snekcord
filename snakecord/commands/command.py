from asyncio import iscoroutine

from .exceptions import InvokeGuardFailure
from .parsers import FunctionArgParser, StringParser
from ..utils import undefined


class InvokeGuard:
    def __init__(self, func):
        self.func = func

    async def __call__(self, *args, **kwargs):
        ret = self.func(*args, **kwargs)
        if iscoroutine(ret):
            ret = await ret
        return ret


class Command:
    def __init__(self, func, *, name=None, description=None, guards=None, overflow=False):
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__
        self.guards = guards or []

        args = FunctionArgParser(func)

        self.vararg = args.vararg
        self.varkwargs = args.varkwarg

        assert not (self.vararg and overflow), "can't have variadic positional argument with overflow"

        if overflow:
            self.overflow = args.kw_only.pop()
        else:
            self.overflow = None

        self.flags = {arg.name: arg for arg in args.kw_only}
        self.args = {arg.name: arg for arg in (args.pos_only + args.pos_or_kw)[1:]}

    async def call_guards(self, message):
        for guard in self.guards:
            ret = await guard(message)
            if ret is False:
                raise InvokeGuardFailure('InvokeGuard {!r} returned False'.format(guard))

    async def invoke(self, message):
        await self.call_guards(message)

        parser = StringParser(message.content)

        args = []
        call_kwargs = {}

        while True:
            position = parser.buffer.tell()
            try:
                char = parser.get()
            except EOFError:
                break
            if char == '-':
                name = parser.read_until('=', '').strip()
                if not self.varkwargs and name not in self.flags:
                    parser.buffer.seek(position)
                else:
                    value = parser.get_argument()
                    call_kwargs[name] = value
                    continue
            elif char in (' ', '\t', '\r', '\n'):
                continue
            else:
                parser.buffer.seek(position)

            if not self.vararg and len(args) == len(self.args):
                break

            args.append(parser.get_argument())

        call_args = [message]

        if not self.vararg:
            for arg in self.args.values():
                try:
                    call_args.append(args.pop(0))
                except IndexError:
                    if arg.optional:
                        default = None if arg.default is not undefined else arg.default
                        args.append(default)
                    else:
                        raise
        else:
            call_args.extend(args)

        if self.overflow is not None:
            call_kwargs[self.overflow.name] = parser.buffer.read()

        await self(*call_args, **call_kwargs)

    async def __call__(self, *args, **kwargs):
        ret = self.func(*args, **kwargs)
        if iscoroutine(ret):
            await ret
