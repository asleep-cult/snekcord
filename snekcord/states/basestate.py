__all__ = ('BaseState', 'BaseSubState')


class _StateCommon:
    def __contains__(self, value):
        raise NotImplementedError

    def get_all(self, keys, fail=False):
        for key in keys:
            try:
                yield self[key]
            except KeyError:
                if fail:
                    raise

    def first(self, func=None):
        for value in self:
            if func is None or func(value):
                return value
        return None


class BaseState(_StateCommon):
    _mapping_ = dict

    def __init__(self, *, client):
        self.client = client
        self.mapping = self._mapping_()

    def __iter__(self):
        return iter(self.mapping.values())

    def __reversed__(self):
        return reversed(self.mapping.values())

    def __getitem__(self, key):
        return self.mapping[key]

    def __len__(self):
        return len(self.mapping)

    def __repr__(self):
        return f'<{self.__class__.__name__} len({len(self)})>'

    def get(self, key):
        return self.mapping.get(key)

    def keys(self):
        return self.mapping.keys()

    def values(self):
        return self.mapping.values()

    def items(self):
        return self.mapping.items()

    def upsert(self, *args, **kwargs):
        raise NotImplementedError

    def clear(self):
        self.mapping.clear()


class BaseSubState(_StateCommon):
    def __init__(self, *, superstate):
        self.superstate = superstate
        self._keys = set()

    def __iter__(self):
        for key in tuple(self._keys):
            try:
                value = self.superstate[key]
            except KeyError:
                continue
            else:
                yield value

    def __reversed__(self):
        for key in reversed(tuple(self._keys)):
            try:
                yield self.superstate[key]
            except KeyError:
                continue

    def __getitem__(self, key):
        if key not in self._keys:
            raise KeyError(key)
        return self.superstate[key]

    def __len__(self):
        return len(self._keys)

    def __repr__(self):
        return f'<{self.__class__.__name__} len({len(self)}), superstate={self.superstate!r}>'

    def get(self, key, default=None):
        if key not in self._keys:
            return default
        return self.superstate.get(key, default)

    def keys(self):
        yield from tuple(self._keys)

    def add_key(self, key):
        self._keys.add(key)

    def remove_key(self, key):
        try:
            self._keys.remove(key)
        except KeyError:
            pass

    def values(self):
        yield from self

    def items(self):
        for key in self._keys:
            try:
                value = self.superstate[key]
            except KeyError:
                continue
            else:
                yield key, value
