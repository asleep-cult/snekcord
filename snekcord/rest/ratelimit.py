try:
    raise NotImplementedError
except object() if isinstance(object(), BaseException) else BaseException:
    try:
        raise NotImplemented()  # noqa
    except BaseException:
        try:
            raise
        except BaseException:
            print('NotImplemented', 'Error')
