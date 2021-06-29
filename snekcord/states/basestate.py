from ..utils import undefined

__all__ = ('BaseState', 'BaseSubState')


class _StateCommon:
    def first(self, func=None):
        for value in self:
            if func is None or func(value):
                return value
        return None


class BaseState(_StateCommon):
    __key_transformer__ = None
    __mapping__ = dict

    def __init__(self, *, client):
        self.client = client
        self.mapping = self.__mapping__()

    def transform_key(self, key):
        if self.__key_transformer__ is None:
            return key
        return self.__key_transformer__(key)

    def __len__(self):
        return self.__mapping__.__len__(self.mapping)

    def __iter__(self):
        return iter(self.values())

    def __reversed__(self):
        return reversed(self.values())

    def __contains__(self, key):
        try:
            key = self.transform_key(key)
        except Exception:
            return False
        return self.__mapping__.__contains__(self.mapping, key)

    def __getitem__(self, key):
        try:
            key = self.transform_key(key)
        except Exception:
            raise KeyError(key)
        return self.__mapping__.__getitem__(self.mapping, key)

    def __setitem__(self, key, value):
        try:
            key = self.transform_key(key)
        except Exception:
            raise ValueError(f'{key!r} is not a valid key')
        return self.__mapping__.__setitem__(self.mapping, key, value)

    def __delitem__(self, key):
        try:
            key = self.transform_key(key)
        except Exception:
            raise ValueError(f'{key!r} is not a valid key')
        return self.__mapping__.__delitem__(self.mapping, key)

    def __repr__(self):
        return f'<{self.__class__.__name__} length={len(self)}>'

    def keys(self):
        return self.__mapping__.keys(self.mapping)

    def values(self):
        return self.__mapping__.values(self.mapping)

    def items(self):
        return self.__mapping__.items(self.mapping)

    def get(self, key, default=None):
        try:
            key = self.transform_key(key)
        except KeyError:
            return default
        return self.__mapping__.get(self.mapping, key, default)

    def pop(self, key, default=undefined):
        try:
            key = self.transform_key(key)
        except Exception:
            if default is not undefined:
                raise KeyError(key)
            return default

        if default is not undefined:
            return self.__mapping__.pop(self.mapping, key, default)

        return self.__mapping__.pop(self.mapping, key)

    def clear(self):
        return self.__mapping__.clear(self.mapping)

    def upsert(self, *args, **kwargs):
        raise NotImplementedError

    def upsert_many(self, values, *args, **kwargs):
        return {self.upsert(value, *args, **kwargs) for value in values}

    def upsert_replace(self, *args, **kwargs):
        values = self.upsert_many(*args, **kwargs)
        self.mapping = {self.transform_key(value): value for value in values}
        return values


class BaseSubState(_StateCommon):
    def __init__(self, *, superstate):
        self.superstate = superstate
        self._keys = set()

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        for key in self._keys:
            try:
                yield self.superstate[key]
            except KeyError:
                continue

    def __reversed__(self):
        for key in reversed(tuple(self._keys)):
            try:
                yield self.superstate[key]
            except KeyError:
                continue

    def __contains__(self, key):
        try:
            key = self.superstate.transform_key(key)
        except Exception:
            return False
        return key in self._keys

    def __getitem__(self, key):
        try:
            key = self.superstate.transform_key(key)
        except Exception:
            raise KeyError(key)

        if key not in self._keys:
            raise KeyError(key)

        return self.superstate[key]

    def __repr__(self):
        return (f'<{self.__class__.__name__} length={len(self)},'
                f' superstate={self.superstate!r}>')

    def set_keys(self, keys):
        self._keys = {self.superstate.transform_key(key) for key in keys}

    def add_key(self, key):
        self._keys.add(self.superstate.transform_key(key))

    def extend_keys(self, keys):
        self._keys.update({self.superstate.transform_key(key) for key in keys})

    def keys(self):
        return self._keys

    def values(self):
        return iter(self)

    def items(self):
        for key in self._keys:
            yield key, self.superstate[key]

    def get(self, key, default=None):
        try:
            key = self.superstate.transfork_key(key)
        except Exception:
            return default

        if key not in self._keys:
            return default

        return self.superstate.get(key, default)
