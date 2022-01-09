__all__ = ('undefined',)


class UndefinedType:
    def __repr__(self):
        return '<undefined>'

    def __bool__(self):
        return False


undefined = UndefinedType()
