from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import CommandCannotExecute

if TYPE_CHECKING:
    from .commander import Commander
    from .command import Command
    from .parsers import StringParser
    from ..message import Message

class CommandInvokeEvent:
    def __init__(self, commander: Commander, message: Message, parser: StringParser, prefix: str):
        self.commander = commander
        self.message = message
        self.parser = parser
        self.prefix = prefix
        self.args = []
        self.kwargs = {}
        self.command = None
        self.invoker = self.message.author
        self.channel = self.message.channel
        self.guild = self.message.guild
        self.send = self.channel.send

        try:
            cmd = parser.get_argument()
        except EOFError:
            return
        for name, command in commander.commands.items():
            if cmd == name or cmd in command.aliases:
                self.command = command
    
    def invoke(self):
        if self.command is not None:
            self.command.invoke(self)

class CommandInvokeHandler:
    def __init__(self, name: str):
        self.name = name
    
    def __call__(self, commander: Commander, evnt: CommandInvokeEvent, *args, **kwargs) -> CommandInvokeEvent:

        if not self.command_can_execute(evnt.command, evnt):
            raise CommandCannotExecute("You cannot execute this command")

        return evnt

    def command_can_execute(self, command: Command, evnt: CommandInvokeEvent) -> bool:
        parent = command.parent

        if parent is not None:
            if not self.command_can_execute(parent, evnt):
                return False

        return command.can_execute(evnt)
