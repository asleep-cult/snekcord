__all__ = ('Undefined', 'undefined')


class Undefined:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return '<undefined>'


undefined = Undefined()
