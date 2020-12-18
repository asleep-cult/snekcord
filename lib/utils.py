import json

class JsonStructure:
    # inspired by Go's encoding/json module
    def __init_subclass__(cls):
<<<<<<< HEAD
        cls.json_fields = {}
        
=======
        if not hasattr(cls, 'json_fields'):
            cls.json_fields = {}
>>>>>>> e810744b1df8f73a495827a81b82bb0d3316a894
        for name, value in dict(cls.__dict__).items():
            if isinstance(value, JsonField):
                cls.json_fields[name] = value
                delattr(cls, name)

    @classmethod
    def unmarshal(cls, data, *args, init_class=True, **kwargs):
        if isinstance(data, (str, bytes, bytearray)):
            data = json.loads(data)

        self = object.__new__(cls)
        for name, field in self.json_fields.items():
            try:
                value = field.unmarshal(data[field.name])
                setattr(self, name, value)
<<<<<<< HEAD
            except:  # JsonField.__call__ could raise anything
                setattr(self, name, field.default)

        self.__init__(*args, **kwargs)
=======
            except: 
                setattr(self, name, field.default)
        if init_class:
            self.__init__(*args, **kwargs)
>>>>>>> e810744b1df8f73a495827a81b82bb0d3316a894
        return self

    def to_dict(self):
        dct = {}
<<<<<<< HEAD

        for name in self.json_fields:
            attr = getattr(self, name)
            dct[name] = attr

=======
        for name, field in self.json_fields.items():
            try:
                attr = getattr(self, name)
                value = field.marshal(attr)
                if value is None and field.omitemoty:
                    continue
                dct[name] = value
            except AttributeError:
                continue
>>>>>>> e810744b1df8f73a495827a81b82bb0d3316a894
        return dct

    def marshal(self):
        return json.dumps(self.to_dict())

class JsonField:
    def __init__(self, key, unmarshal_callable=None, marshal_callable=None, default=None, struct=None, init_struct_class=True, omitemoty=True):
        if struct is not None:
            self.unmarshal_callable = lambda *args, **kwargs: struct.unmarshal(*args, **kwargs, init_class=init_struct_class)
            self.marshal_callable = struct.to_dict
        else:
            self.unmarshal_callable = unmarshal_callable
            self.marshal_callable = marshal_callable
        self.name = key
        self.default = default

    def unmarshal(self, data):
        if self.unmarshal_callable is None:
            return data
        return self.unmarshal_callable(data)

    def marshal(self, data):
        if self.marshal_callable is None:
            return data
        return self.marshal_callable(data)

class JsonArray(JsonField):
    def unmarshal(self, data):
        items = []
        for item in data:
            items.append(super().unmarshal(item))
        return items

    def marshal(self, data):
        items = []
        for item in data:
            items.append(super().marshal(item))
        return items