__all__ = ('undefined',)


class _Undefined:
    def __bool__(self):
        return False

    def __repr__(self):
        return '<undefined>'


undefined = _Undefined()
