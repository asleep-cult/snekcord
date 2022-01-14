from reprlib import recursive_repr
from weakref import WeakValueDictionary

from .undefined import undefined


class Collection:
    """An ordered dictionary with support for indexing."""

    __slots__ = ('_keys', '_map')

    def __init__(self):
        self._create_keys()
        self._create_map()

    def _create_keys(self):
        self._keys = []

    def _create_map(self):
        self._map = {}

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        for key in self._keys:
            yield self._map[key]

    def __reversed__(self):
        for key in reversed(self._keys):
            yield self._map[key]

    def __eq__(self, other):
        if not isinstance(other, Collection):
            return NotImplementedError

        if self is other:
            return True

        return self._map == other._map and self._keys == other._keys

    @recursive_repr('Collection({...})')
    def __repr__(self):
        return f'Collection({self._map})'

    def keys(self):
        return CollectionKeysView(self)

    def values(self):
        return CollectionValuesView(self)

    def items(self):
        return CollectionItemsView(self)

    def get(self, key, default=None):
        return self._map.get(key, default)

    def getkey(self, index):
        try:
            return self._keys[index]
        except IndexError:
            raise IndexError('collection keys index out of range') from None

    def pop(self, key, default=undefined):
        try:
            value = self._map.pop(key)
        except KeyError:
            if default is undefined:
                raise
        else:
            self._keys.remove(key)
            return value

        return default

    def popitem(self, last=True):
        if not self:
            raise KeyError('popitem(): collection is empty')

        key = self._map.pop(-1 if last else 0)
        value = self._map.pop(key)

        return key, value

    def setdefault(self, key, default):
        try:
            return self._map[key]
        except KeyError:
            self._map[key] = default
            self._keys.append(key)
            return default

    def update(self, map=None, **kwargs):
        if map is not None:
            for key, value in map.items():
                self[key] = value

        for key, value in kwargs.items():
            self[key] = value

    def clear(self):
        self._keys.clear()
        self._map.clear()

    def copy(self):
        other = self.__class__()
        other._keys = self._keys.copy()
        other._map = self._map.copy()
        return other

    def __ior__(self, other):
        self.update(other)
        return self

    def __or__(self, other):
        if not isinstance(other, Collection):
            return NotImplemented

        copy = self.copy()
        copy.update(other)
        return copy

    def __ror__(self, other):
        if not isinstance(other, Collection):
            return NotImplemented

        copy = other.copy()
        copy.update(self)
        return copy

    def __contains__(self, value):
        return value in self._map.values()

    def __getitem__(self, index):
        return self._map[self.getkey(index)]

    def __setitem__(self, key, value):
        self._map[key] = value

    def __delitem__(self, index):
        del self._map[self.getkey(index)]


class WeakCollection(Collection):
    def _create_map(self):
        self._map = WeakValueDictionary()


class CollectionKeysView:
    def __init__(self, collection):
        self._collection = collection

    def __len__(self):
        return len(self._collection)

    def __iter__(self):
        yield from self._collection._keys

    def __reversed__(self):
        yield from reversed(self._collection._keys)

    def __contains__(self, key):
        return key in self._collection._map.keys()

    def __eq__(self, other):
        if not isinstance(other, CollectionKeysView):
            return NotImplemented

        if self._collection is other._collection:
            return True

        return self._collection._keys == other._collection._keys


class CollectionValuesView:
    def __init__(self, collection):
        self._collection = collection

    def __len__(self):
        return len(self._collection)

    def __iter__(self):
        return iter(self._collection)

    def __reversed__(self):
        return reversed(self._collection)

    def __contains__(self, value):
        return value in self._collection

    def __eq__(self, other):
        if not isinstance(other, CollectionValuesView):
            return NotImplemented

        if self._collection is other._collection:
            return True

        return all(self._collection[i] == other._collection[i] for i in range(len(self)))


class CollectionItemsView:
    def __init__(self, collection):
        self._collection = collection

    def __len__(self):
        return len(self._collection)

    def __iter__(self):
        for key in self._collection._keys:
            value = self._collection._map[key]
            yield key, value

    def __reversed__(self):
        for key in reversed(self._collection._keys):
            value = self._collection._map[key]
            yield key, value

    def __contains__(self, item):
        if not isinstance(item, tuple) or len(item) != 2:
            return False

        try:
            return self._collection._map[item[0]] == item[1]
        except KeyError:
            return False

    def __eq__(self, other):
        if not isinstance(other, CollectionItemsView):
            return NotImplemented

        return self._collection == other._collection
