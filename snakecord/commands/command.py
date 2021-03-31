from ..utils import undefined

WHITESPACE = (' ', '\t', '\r', '\n')


class Command:
    def __init__(self, commander, name, args, *, description=None, overflow=False):
        self.commander = commander
        self.name = name
        self.description = description

        self.vararg = args.vararg
        self.varkwargs = args.varkwarg

        assert not (self.vararg and overflow), "can't have variadic positional argument with overflow"

        if overflow:
            self.overflow = args.kw_only.pop()
        else:
            self.overflow = None

        self.flags = {arg.name: arg for arg in args.kw_only}
        self.args = {arg.name: arg for arg in (args.pos_only + args.pos_or_kw)[1:]}

    def _parse_args(self, evnt):
        parser = evnt.parser

        args = []

        while True:
            position = parser.buffer.tell()
            try:
                char = parser.get()
            except EOFError:
                break
            if char == '-':
                name = parser.read_until(('=', *WHITESPACE), '').strip()
                if not self.varkwargs and name not in self.flags:
                    parser.buffer.seek(position)
                else:
                    value = parser.get_argument()
                    evnt.kwargs[name] = value
                    continue
            elif char in WHITESPACE:
                continue
            else:
                parser.buffer.seek(position)

            if not self.vararg and len(args) == len(self.args):
                break

            args.append(parser.get_argument())

        if not self.vararg:
            for arg in self.args.values():
                try:
                    evnt.args.append(args.pop(0))
                except IndexError:
                    if arg.optional:
                        default = None if arg.default is not undefined else arg.default
                        args.append(default)
                    else:
                        raise
        else:
            evnt.args.extend(args)

        if self.overflow is not None:
            evnt.kwargs[self.overflow.name] = parser.buffer.read()

    def invoke(self, evnt):
        self._parse_args(evnt)
        self.commander.push_event('invoke_{}'.format(self.name), evnt, *evnt.args, **evnt.kwargs)
