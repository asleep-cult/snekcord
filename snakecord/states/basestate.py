class BaseState:
    __key_transformer__ = None

    def __init__(self, *, manager):
        self.manager = manager

    def transform_key(self, key):
        if self.__key_transformer__ is None:
            return key
        return self.__key_transformer__(key)

    async def new(self, *args, **kwargs):
        raise NotImplementedError

    async def extend_new(self, values, *args, **kwargs):
        return [await self.new(value, *args, **kwargs) for value in values]

    async def get(self, key, default=None):
        raise NotImplementedError

    async def set(self, key, value):
        raise NotImplementedError

    async def delete(self, key):
        raise NotImplementedError

    async def has(self, value):
        raise NotImplementedError

    async def first(self, func=None):
        raise NotImplementedError

    async def size(self):
        raise NotImplementedError

    async def clear(self):
        raise NotImplementedError

    def __aiter__(self):
        raise NotImplementedError


class MutableMappingState(BaseState):
    __mapping__ = dict

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mapping = self.__mapping__()

    async def get(self, key, default=None):
        return self.mapping.get(self.transform_key(key), default)

    async def set(self, key, value):
        self.mapping[self.transform_key(key)] = value

    async def delete(self, key):
        del self.mapping[self.transform_key(key)]

    async def has(self, key):
        return key in self.mapping.values()

    async def first(self, func=None):
        for value in self.mapping.values():
            if func is None or func(value):
                return value

    async def size(self):
        return len(self)

    async def clear(self):
        return self.mapping.clear()

    async def __aiter__(self):
        for value in self.mapping.values():
            yield value

    @classmethod
    def for_base(cls, klass):
        return type(klass.__name__, (klass, cls), {})


class BaseSubState:
    def __init__(self, superstate):
        self.superstate = superstate
        self._keys = set()

    def set_keys(self, keys):
        self._keys = {self.superstate.transform_key(key) for key in keys}

    def add_key(self, key):
        self._keys.add(self.superstate.transform_key(key))

    def remove_key(self, key):
        self._keys.remove(self.superstate.transform_key(key))

    def update_keys(self, keys):
        self._keys.update({self.superstate.transform_key(key) for key in keys})

    def key_for(self, value):
        raise NotImplementedError

    async def get(self, key, default=None):
        value = await self.superstate.get(key)
        if self.key_for(value) not in self._keys:
            return default
        return value

    async def __aiter__(self):
        for key in self._keys:
            yield await self.superstate.get(key)
