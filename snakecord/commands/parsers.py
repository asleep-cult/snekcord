import inspect
import typing
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
        self.separator = separator
        self.wrap_table = wrap_table

    def get(self):
        return self.buffer.read(1)

    def backup(self, amount=1):
        position = self.buffer.tell() - amount
        self.buffer.seek(position)

    def get_argument(self):
        string = self.get()
        terminator = self.wrap_table.get(string)

        if terminator is not None:
            string = ''
        else:
            terminator = self.separator

        while True:
            char = self.get()
            if char == terminator:
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
        return self.default is not undefined or origin is typing.Optional


class FunctionArgParser:
    def __init__(self, func):
        self.func = func
        self.signiature = inspect.signature(func)
        self.pos_only = []
        self.pos_or_kw = []
        self.kw_only = []

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
            elif param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY):
                args = self.pos_or_kw
            elif param.kind in (param.KEYWORD_ONLY, param.VAR_KEYWORD):
                args = self.kw_only

            args.append(arg)

        if not self.pos_or_kw:
            self.pos_or_kw = self.pos_only
