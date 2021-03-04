from ..client import Client
from .command import Command
from typing import List

class CommandClient(Client):
    def __init__(self, prefix: str, *args, **kwargs):
        self._commands: List[Command] = []
        super().__init__(*args, **kwargs)