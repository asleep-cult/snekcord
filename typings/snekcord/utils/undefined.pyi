from typing import Final, Literal

class _Undefined:
    def __bool__(self) -> Literal[False]: ...
    def __repr__(self) -> Literal['<undefined>']: ...

undefined: Final[_Undefined]
