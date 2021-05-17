import json

__all__ = ('JsonTemplate', 'JsonField', 'JsonArray', 'JsonObject')


class JsonTemplate:
    def __init__(self, *, __extends__=(), **fields):
        self.local_fields = fields
        self.fields = self.local_fields.copy()

        for template in __extends__:
            self.fields.update(template.fields)

    def update(self, obj, data, *, set_defaults=False):
        for name, field in self.fields.items():
            try:
                value = field.unmarshal(data[field.key])
                setattr(obj, name, value)
            except Exception:
                if set_defaults:
                    setattr(obj, name, field.default())

    def to_dict(self, obj):
        data = {}

        for name, field in self.fields.items():
            value = getattr(obj, name, field.default())

            if value is None and field.omitempty:
                continue

            try:
                value = field.marshal(value)
            except Exception:
                continue

            if value is None and field.omitempty:
                continue

            data[field.key] = value

        return data

    def marshal(self, obj, *args, **kwargs):
        return json.dumps(self.to_dict(obj), *args, **kwargs)

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

    def unmarshal(self, value):
        if self._unmarshal is not None:
            value = self._unmarshal(value)
        return value

    def marshal(self, value):
        if self._marshal is not None:
            value = self._marshal(value)
        return value

    def default(self):
        if callable(self._default):
            return self._default()
        return self._default


class JsonArray(JsonField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', list)
        super().__init__(*args, **kwargs)

    def unmarshal(self, values):
        unmarshal = super().unmarshal
        return [unmarshal(value) for value in values]

    def marshal(self, values):
        marshal = super().marshal
        return [marshal(value) for value in values]


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
    def __json_init__(self, *args, **kwargs):
        pass

    @classmethod
    def unmarshal(cls, data=None, *args, **kwargs):
        if cls.__template__ is None:
            raise NotImplementedError

        if isinstance(data, (bytes, bytearray, memoryview, str)):
            data = json.loads(data)

        self = cls.__new__(cls)
        cls.__json_init__(self, *args, **kwargs)

        if data is not None:
            self.update(data, set_defaults=True)

        return self

    def update(self, *args, **kwargs):
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.update(self, *args, **kwargs)

    def to_dict(self, *args, **kwargs):
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.to_dict(self, *args, **kwargs)

    def marshal(self, *args, **kwargs):
        if self.__template__ is None:
            raise NotImplementedError
        return self.__template__.marshal(self, *args, **kwargs)
