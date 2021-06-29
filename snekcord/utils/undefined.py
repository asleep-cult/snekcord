__all__ = ('Undefined', 'undefined')


class Undefined:
    def __bool__(self):
        return False

    def __repr__(self):
        return '<undefined>'


undefined = Undefined()
