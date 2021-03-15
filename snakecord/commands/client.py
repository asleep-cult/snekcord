from ..client import Client
from .parsers import StringParser, FunctionArgParser


class CommanderClient(Client):
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix
