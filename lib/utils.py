import json

class JsonStructure:
    #inspired by Go's encoding/json module
    def __init_subclass__(cls):
        cls.json_fields = {}
        for name, value in dict(cls.__dict__).items():
            if isinstance(value, JsonField):
                cls.json_fields[name] = value

    @classmethod
    def unmarshal(cls, data, *args, **kwargs):
        if isinstance(data, (str, bytes, bytearray)):
            data = json.loads(data)
        self = object.__new__(cls)
        for name, field in self.json_fields.items():
            try:
                value = field(data[field.name])
                setattr(self, name, value)
            except: #JsonField.__call__ could raise anything
                setattr(self, name, field.default)
        self.__init__(*args, **kwargs)
        return self

    def to_dict(self):
        dct = {}
        for name in self.json_fields:
            attr = getattr(self, name)
            dct[name] = attr
        return dct

    def marshal(self):
        return json.dumps(self.to_dict())

class JsonField:
    def __init__(self, type_callable, key, default=None):
        self.type_callable = type_callable
        self.name = key
        self.default = default

    def __call__(self, data):
        if self.type_callable is None:
            return data
        return self.type_callable(data)