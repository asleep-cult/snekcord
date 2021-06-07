import typing as t

__all__ = ('undefined',)


class _Undefined:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return '<undefined>'


if t.TYPE_CHECKING:
    undefined = t.NewType('undefined', _Undefined)
else:
    undefined = _Undefined()
