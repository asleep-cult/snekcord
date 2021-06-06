from typing import Literal

__all__ = ('undefined',)


class _Undefined:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> Literal['<undefined>']:
        return '<undefined>'


undefined = _Undefined()
