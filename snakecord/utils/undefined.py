class _Undefined:
    def __repr__(self):
        return '<undefined>'

    def __bool__(self):
        return False


undefined = _Undefined()
