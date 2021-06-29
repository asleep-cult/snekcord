import typing as t

__all__ = ('Undefined', 'undefined')


class Undefined:
    def __bool__(self) -> t.Literal[False]: ...


undefined: Undefined
