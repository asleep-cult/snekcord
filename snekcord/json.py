import json
from collections.abc import Iterable
from typing import Any, Dict

JSONObject = Dict[str, Any]


class JSONEncoder(json.JSONEncoder):
    """A subclass of json.JSONEncoder that treats any iterable object as an array."""

    def __init__(self, *, separators=(',', ':'), **kwargs):
        super().__init__(separators=separators, **kwargs)

    def default(self, obj):
        if isinstance(obj, Iterable):
            return tuple(obj)

        return super().default(obj)


def load_json(*args, **kwargs):
    """Equivalent to json.loads."""
    return json.loads(*args, **kwargs)


def dump_json(obj, *, separators=(',', ':'), **kwargs):
    """Equivalent to json.dumps using the library's JSONEncoder class."""
    return json.dumps(obj, separators=separators, **kwargs, cls=JSONEncoder)
