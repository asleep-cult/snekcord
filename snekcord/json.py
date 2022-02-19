import json
import typing

__all__ = (
    'load_json',
    'dump_json',
)

T = typing.TypeVar('T')

JSONObject = typing.Dict[str, typing.Any]
JSONType = typing.Union[JSONObject, str, int, float, typing.List[typing.Any]]


def dump_default(
    object: typing.Union[typing.Iterable[T], typing.Any]
) -> typing.Union[typing.Tuple[T, ...], typing.Any]:
    if isinstance(object, typing.Iterable):
        return tuple(object)

    raise TypeError(f'Object of type {object.__class__.__name__} is not JSON serializable')


def load_json(*args: typing.Union[str, bytes], **kwargs: typing.Any) -> typing.Any:
    """Equivalent to json.loads."""
    return json.loads(*args, **kwargs)


def dump_json(
    obj: typing.Any, *, separators: typing.Tuple[str, str] = (',', ':'), **kwargs: typing.Any
) -> str:
    """Equivalent to json.dumps but converts any iterable object to a tuple."""
    return json.dumps(obj, separators=separators, **kwargs, default=dump_json)
