import json

from .misc import maybe_await

__all__ = ('JsonTemplate', 'JsonField', 'JsonArray', 'JsonObject')


class JsonTemplate:
    def __init__(self, *, __extends__=(), **fields):
        self.local_fields = fields
        self.fields = self.local_fields.copy()

        for template in __extends__:
            self.fields.update(template.fields)

    async def update(self, obj, data, *, set_defaults=False):
        for name, field in self.fields.items():
            try:
                value = await field.unmarshal(data[field.key])
                setattr(obj, name, value)
            except Exception:
                if set_defaults:
                    setattr(obj, name, await field.default())

    async def to_dict(self, obj):
        data = {}

        for name, field in self.fields.items():
            value = getattr(obj, name, await field.default())

            if value is None and field.omitempty:
                continue

            try:
                value = await field.marshal(value)
            except Exception:
                continue

            if value is None and field.omitempty:
                continue

            data[field.key] = value

        return data

    async def marshal(self, obj, *args, **kwargs):
        return json.dumps(await self.to_dict(obj), *args, **kwargs)

    def default_object(self, name='GenericObject'):
        return JsonObjectMeta(name, (JsonObject,), {},
                              template=self)


class JsonField:
    def __init__(self, key, unmarshal=None, marshal=None, object=None,
                 default=None, omitempty=False):
        self.key = key
        self.object = object
        self.omitempty = omitempty
        self._default = default

        if self.object is not None:
            self._unmarshal = self.object.unmarshal
            self._marshal = self.object.__template__.to_dict
        else:
            self._unmarshal = unmarshal
            self._marshal = marshal

    async def unmarshal(self, value):
        if self._unmarshal is not None:
            value = await maybe_await(self._unmarshal(value))
        return value

    async def marshal(self, value):
        if self._marshal is not None:
            value = await maybe_await(self._marshal(value))
        return value

    async def default(self):
        if callable(self._default):
            return await maybe_await(self._default())
        return self._default


class JsonArray(JsonField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', list)
        super().__init__(*args, **kwargs)

    async def unmarshal(self, values):
        return [await super(JsonArray, self).unmarshal(value)
                for value in values]

    async def marshal(self, values):
        return [await super(JsonArray, self).marshal(value)
                for value in values]


def _flatten_slots(cls, slots=None):
    if slots is None:
        slots = set()

    slots.update(getattr(cls, '__slos__', ()))

    for base in cls.__bases__:
        _flatten_slots(base, slots)

    return slots


class JsonObjectMeta(type):
    def __new__(mcs, name, bases, attrs, template=None):
        external_slots = set()
        for base in bases:
            _flatten_slots(base, external_slots)

        slots = tuple(attrs.get('__slots__', ()))
        if template is not None:
            fields = template.fields
            slots += tuple(field for field in fields
                           if field not in slots
                           and field not in external_slots)

        attrs['__slots__'] = slots
        attrs['__template__'] = template

        return type.__new__(mcs, name, bases, attrs)


class JsonObject(metaclass=JsonObjectMeta):
    async def __json_init__(self, *args, **kwargs):
        pass

    @classmethod
    async def unmarshal(cls, data=None, *args, **kwargs):
        if cls.__template__ is None:
            raise NotImplementedError

        if isinstance(data, (bytes, bytearray, memoryview, str)):
            data = json.loads(data)

        self = cls.__new__(cls)
        await cls.__json_init__(self, *args, **kwargs)

        if data is not None:
            await self.update(data, set_defaults=True)

        return self

    async def update(self, *args, **kwargs):
        if self.__template__ is None:
            raise NotImplementedError
        return await self.__template__.update(self, *args, **kwargs)

    async def to_dict(self, *args, **kwargs):
        if self.__template__ is None:
            raise NotImplementedError
        return await self.__template__.to_dict(self, *args, **kwargs)

    async def marshal(self, *args, **kwargs):
        if self.__template__ is None:
            raise NotImplementedError
        return await self.__template__.marshal(self, *args, **kwargs)
