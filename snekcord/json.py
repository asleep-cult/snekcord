import json
import typing

__all__ = (
    'JSONEncoder',
    'load_json',
    'dump_json',
)

T = typing.TypeVar('T')
JSONObject = typing.Dict[str, typing.Any]


class JSONEncoder(json.JSONEncoder):
    """A subclass of json.JSONEncoder that treats any iterable object as an array."""

    def __init__(
        self, *, separators: typing.Tuple[str, str] = (',', ':'), **kwargs: typing.Any
    ) -> None:
        super().__init__(separators=separators, **kwargs)

    def default(
        self, o: typing.Union[typing.Iterable[T], typing.Any]
    ) -> typing.Union[typing.Tuple[T, ...], typing.Any]:
        if isinstance(o, typing.Iterable):
            return tuple(o)

        return super().default(o)


def load_json(*args: typing.Union[str, bytes], **kwargs: typing.Any) -> typing.Any:
    """Equivalent to json.loads."""
    return json.loads(*args, **kwargs)


def dump_json(
    obj: typing.Any, *, separators: typing.Tuple[str, str] = (',', ':'), **kwargs: typing.Any
) -> str:
    """Equivalent to json.dumps using the library's JSONEncoder class."""
    return json.dumps(obj, separators=separators, **kwargs, cls=JSONEncoder)
