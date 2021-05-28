import weakref

__all__ = ('BaseState', 'BaseSubState')


class _StateCommon:
    def first(self, func=None):
        for value in self:
            if func is None or func(value):
                return value


class BaseState(_StateCommon):
    __key_transformer__ = None
    __mapping__ = dict
    __recycle_enabled__ = True
    __recycled_mapping__ = weakref.WeakValueDictionary

    def __init__(self, *, manager):
        self.manager = manager
        self.mapping = self.__mapping__()
        if self.__recycle_enabled__:
            self.recycle_bin = self.__recycled_mapping__()

    def transform_key(self, key):
        if self.__key_transformer__ is None:
            return key
        return self.__key_transformer__(key)

    def __len__(self):
        return self.__mapping__.__len__(self.mapping)

    def __iter__(self):
        return iter(self.values())

    def __reversed__(self):
        return self.__mapping__.__reversed__(self.mapping)

    def __contains__(self, key):
        return self.__mapping__.__contains__(
            self.mapping, self.transform_key(key))

    def __getitem__(self, key):
        return self.__mapping__.__getitem__(
            self.mapping, self.transform_key(key))

    def __setitem__(self, key, value):
        return self.__mapping__.__setitem__(
            self.mapping, self.transform_key(key), value)

    def __delitem__(self, key):
        return self.__mapping__.__delitem__(
            self.mapping, self.transform_key(key))

    def __repr__(self):
        attrs = [('length', len(self))]

        if self.__recycle_enabled__:
            attrs.append(('recycled', len(self.recycle_bin)))

        formatted = ', '.join(f'{name}={value}' for name, value in attrs)
        return f'{self.__class__.__name__}({formatted})'

    def keys(self):
        return self.__mapping__.keys(self.mapping)

    def values(self):
        return self.__mapping__.values(self.mapping)

    def items(self):
        return self.__mapping__.items(self.mapping)

    def get(self, key):
        return self.__mapping__.get(self.mapping, self.transform_key(key))

    def pop(self, key, *args, **kwargs):
        return self.__mapping__.pop(self.mapping, self.transform_key(key),
                                    *args, **kwargs)

    def popitem(self):
        return self.__mapping__.popitem(self.mapping)

    def new(self, *args, **kwargs):
        raise NotImplementedError

    def new_ex(self, values, *args, **kwargs):
        return [self.new(value, *args, **kwargs) for value in values]

    def recycle(self, key, value):
        if self.__recycle_enabled__:
            return self.__recycled_mapping__.__setitem__(
                self.recycle_bin, self.transform_key(key), value)

    def unrecycle(self, key, *args, **kwargs):
        if self.__recycle_enabled__:
            return self.__recycled_mapping__.pop(
                self.recycle_bin, self.transform_key(key), *args, **kwargs)


class BaseSubState:
    def __init__(self, *, superstate):
        self.superstate = superstate
        self._keys = set()

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        for key in self._keys:
            yield self.superstate[key]

    def __reversed__(self):
        for key in reversed(self._keys):
            yield self.superstate[key]

    def __contains__(self, key):
        return self.superstate.transform_key(key) in self._keys

    def __getitem__(self, key):
        return self.superstate[key]

    def __repr__(self):
        return (f'{self.__class__.__name__}(length={len(self)},'
                f' superstate={self.superstate!r})')

    def set_keys(self, keys):
        self._keys = {self.superstate.transform_key(key) for key in keys}

    def add_key(self, key):
        self._keys.add(self.superstate.transform_key(key))

    def extend_keys(self, keys):
        self._keys.update({self.superstate.transform_key(key) for key in keys})

    def remove_key(self, key):
        self._keys.remove(self.superstate.transform_key(key))

    def key_for(self, value):
        raise NotImplementedError

    def keys(self):
        return self._keys

    def values(self):
        return iter(self)

    def items(self):
        for key in self._keys:
            yield key, self.superstate[key]

    def get(self, key):
        return self.superstate.get(key)
