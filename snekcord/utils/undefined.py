__all__ = ('undefined',)


class _Undefined:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return '<undefined>'


undefined = _Undefined()
