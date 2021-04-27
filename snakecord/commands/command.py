from __future__ import annotations

from string import whitespace
from typing import Iterable, NoReturn, Optional, TYPE_CHECKING, Tuple, Type, Union

from .parsers import FunctionArgParser
from ..utils import undefined

if TYPE_CHECKING:
    from .commander import Commander
    from .events import CommandInvokeEvent


class CommandMeta(type):

    def __new__(
        cls,
        cls_name: str,
        bases: Tuple[type],
        attrs: dict,
        *,
        name: Optional[str] = None,
        auto_register: bool = False,
        overflow: bool = False,
        aliases: Iterable[str] = (),
        slash: bool = False,
        pass_event: bool = True
    ) -> CommandMeta:
        self = type.__new__(cls, cls_name, bases, attrs)

        args = FunctionArgParser(self.execute)

        self.__command_vararg__ = vararg = args.vararg
        self.__command_varkwarg__ = args.varkwarg

        assert not (vararg and overflow), "can't have variadic positional argument with overflow"

        if overflow:
            overflow = args.kw_only.pop()
        else:
            overflow = None

        flags = {arg.name: arg for arg in args.kw_only}
        args = {arg.name: arg for arg in (args.pos_only + args.pos_or_kw)[1:]}

        self.name = name
        self.description = self.__doc__
        self.aliases = [] if aliases is None else list(aliases)
        self.subcommands = []

        self.__command_overflow__ = overflow
        self.__command_auto_register__ = auto_register
        self.__command_args__ = args
        self.__command_flags__ = flags
        self.__command_slash__ = slash
        self.__command_pass_event__ = pass_event
        self.parent = None
        return self

class Command(metaclass=CommandMeta):
    def __init__(self, commander: Commander):
        self.commander = commander

    def execute(self, *args, **kwargs) -> NoReturn:
        raise NotImplementedError

    def can_execute(self, evnt: CommandInvokeEvent) -> bool:
        return True

    def _parse_args(self, evnt: CommandInvokeEvent) -> None:
        parser = evnt.parser

        args = []

        while True:
            position = parser.buffer.tell()
            try:
                char = parser.get()
            except EOFError:
                break
            if char == '-':
                name = parser.read_until(('=', *whitespace), '').strip()
                if not self.__command_varkwargs__ and name not in self.__command_flags__:
                    parser.buffer.seek(position)
                else:
                    value = parser.get_argument()
                    evnt.kwargs[name] = value
                    continue
            elif char in whitespace:
                continue
            else:
                parser.buffer.seek(position)

            if not self.__command_vararg__ and len(args) == len(self.__command_args__):
                break

            args.append(parser.get_argument())

        if not self.__command_vararg__:
            for index, arg in enumerate(self.__command_args__.values()):
                try:
                    evnt.args.append(args.pop(0))
                except IndexError:
                    if arg.optional:
                        default = None if arg.default is not undefined else arg.default
                        args.append(default)
                    elif not (index == 0 and self.__command_pass_event__):
                        raise
        else:
            evnt.args.extend(args)

        overflow = self.__command_overflow__

        if overflow is not None:
            evnt.kwargs[overflow.name] = parser.buffer.read()

    def invoke(self, evnt):
        self._parse_args(evnt)
        self.commander.push_event('invoke_{}'.format(self.name), evnt, *evnt.args, **evnt.kwargs)

    @classmethod
    def register(cls, commander: Commander) -> Command:
        cmd = cls(commander)
        if cls.__command_slash__:
            raise NotImplementedError

        commander.register_command(cmd)
        return cmd

    @classmethod
    def subcommand(cls, other_cls: Union[Command, Type[Command]]):
        cls.add_subcommand(other_cls)
        return other_cls

    @classmethod
    def add_alias(cls, alias):
        if not isinstance(alias, str):
            raise ValueError('Alias must be a str.')

        elif alias in cls.aliases:
            raise ValueError('This is already an existing alias.')

        cls.aliases.append(alias)

    @classmethod
    def add_subcommand(cls, command: Union[Type[Command], Command]):
        if command.parent is not None:
            raise ValueError('This command is already a subcommand.')

        command.parent = cls
        command.subcommands.append(command)
