import inspect
import typing
from types import FunctionType
from io import StringIO

from ..utils import undefined

WRAP_TABLE = {
    '\'': '\'',
    '"': '"',
    '`': '`',
    '‘': '’',
    '“': '”',
    "«": "»"
}


class StringParser:
    def __init__(self, string, separator=' ', wrap_table=WRAP_TABLE):
        self.buffer = StringIO(string)
        self.string = string
        self.separator = separator
        self.wrap_table = wrap_table

    def get(self):
        if self.buffer.tell() >= len(self.string):
            raise EOFError
        return self.buffer.read(1)

    def get_argument(self):
        string = self.get()
        terminator = self.wrap_table.get(string)

        if terminator is not None:
            string = ''
        else:
            terminator = self.separator

        string = self.read_until(terminator, string)

        return string

    def read_until(self, terminator, string):
        if isinstance(terminator, str):
            terminator = (terminator,)
        while True:
            try:
                char = self.get()
            except EOFError:
                break
            if char in terminator:
                break
            string += char
        return string


class Argument:
    def __init__(self, name, annotation, default):
        self.name = name
        self.annotation = annotation
        self.default = default

    @property
    def optional(self):
        origin = getattr(self.annotation, '__origin__', self.annotation)
        return self.default is not undefined or type(None) in origin.__args__


class FunctionArgParser:
    def __init__(self, func: FunctionType):
        self.func = func
        self.signiature = inspect.signature(func)
        self.pos_only = []
        self.pos_or_kw = []
        self.kw_only = []
        self.vararg = False
        self.varkwarg = False
        self.parse()

    def parse(self):
        for name, param in self.signiature.parameters.items():
            name = param.name

            annotation = param.annotation
            if annotation == param.empty:
                annotation = undefined

            default = param.default
            if default == param.empty:
                default = undefined

            arg = Argument(name, annotation, default)

            if param.kind == param.POSITIONAL_ONLY:
                args = self.pos_only
            elif param.kind == param.VAR_POSITIONAL:
                self.vararg = True
            elif param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY):
                args = self.pos_or_kw
            elif param.kind == param.VAR_KEYWORD:
                self.varkwarg = True
            elif param.kind == param.KEYWORD_ONLY:
                args = self.kw_only

            args.append(arg)
