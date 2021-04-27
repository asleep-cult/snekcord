from asyncio import AbstractEventLoop, get_event_loop
from functools import wraps
from importlib import util
import sys
from typing import Dict, Optional
from types import MethodType, ModuleType

from ..gateway import MessageCreateEvent

from .parsers import StringParser
from ..client import Client
from ..events import EventPusher
from .events import CommandInvokeHandler, CommandInvokeEvent
from .command import Command


class Commander(EventPusher):
    def __init__(self, client: Client, prefix: str, *, loop: Optional[AbstractEventLoop] = None):
        super().__init__(loop or get_event_loop())

        self.prefix = prefix
        self.commands: Dict[str, Command] = {}
        self.loaded_files: Dict[str, ModuleType] = {}
        self.client = client
        self.register_listener('message_create', self._handle_message_create)
        self.subscribe(client)

    def register_command(self, cmd: Command):
        if cmd.name in self.commands:
            raise ValueError("This command is already registered.")

        name = f'invoke_{cmd.name}'
        self.commands[cmd.name] = cmd
        self._handlers[name] = CommandInvokeHandler(name)

        self.register_listener(name, self._wrap_callback(cmd.execute))
    
    @staticmethod
    def _wrap_callback(method: MethodType):
        @wraps(method)
        def inner(evnt: CommandInvokeEvent):
            args = list(evnt.args)

            if evnt.command.__command_pass_event__:
                args.insert(0, evnt)

            return method(*args, **evnt.kwargs)

        return inner

    async def _handle_message_create(self, evnt: MessageCreateEvent):
        message = evnt.message

        parser = StringParser(message.content)
        prefix = parser.buffer.read(len(self.prefix))
        event = CommandInvokeEvent(self, message, parser, prefix)

        if prefix != self.prefix:
            return

        event.invoke()

    def load_file(self, name: str, package: Optional[str] = None, call_file_load: bool = True):
        name = util.resolve_name(name, package)

        assert name not in self.loaded_files, "File {!r} is already loaded".format(name)

        spec = util.find_spec(name, package)

        module = util.module_from_spec(spec)

        spec.loader.exec_module(module)

        sys.modules[name] = module

        for value in module.__dict__.values():
            if isinstance(value, type) and issubclass(value, Command) and value.__command_auto_register__:
                value.register(self)

        file_load = getattr(module, 'file_load', None)

        if call_file_load and file_load is not None:
            try:
                file_load(self)
            except Exception:
                del sys.modules[name]
                raise
        
        self.loaded_files[name] = module

