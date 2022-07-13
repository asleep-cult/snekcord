import json
import typing

from .undefined import MaybeUndefined, undefined

__all__ = (
    'load_json',
    'dump_json',
)

T = typing.TypeVar('T')
DefaultT = typing.TypeVar('DefaultT')

JSONObject = typing.Dict[str, 'JSONType']
JSONType = typing.Union[None, bool, str, int, float, JSONObject, typing.List['JSONType']]


def dump_default(
    object: typing.Union[typing.Iterable[T], typing.Any]
) -> typing.Union[typing.Tuple[T, ...], typing.Any]:
    if isinstance(object, typing.Iterable):
        return tuple(object)

    raise TypeError(f'Object of type {object.__class__.__name__} is not JSON serializable')


def load_json(*args: typing.Union[str, bytes], **kwargs: typing.Any) -> JSONType:
    """Equivalent to json.loads."""
    return json.loads(*args, **kwargs)


def dump_json(
    obj: typing.Any, *, separators: typing.Tuple[str, str] = (',', ':'), **kwargs: typing.Any
) -> str:
    """Equivalent to json.dumps but converts any iterable object into a tuple."""
    return json.dumps(obj, separators=separators, **kwargs, default=dump_default)


def json_get(
    data: JSONObject,
    key: str,
    tp: typing.Type[T],
    *,
    default: MaybeUndefined[DefaultT] = undefined,
) -> typing.Union[T, DefaultT]:
    try:
        value = data[key]
    except KeyError:
        if default is undefined:
            raise TypeError(f'{key!r} does not exist')

        return default

    origin = typing.get_origin(tp)

    if origin is typing.Union:
        args = typing.get_args(origin)
        tps = tuple(typing.get_origin(arg) or arg for arg in args)
    else:
        tps = origin if origin is not None else tp

    if not isinstance(value, tps):
        raise TypeError(f'{key!r} should be a {tps!r}, found {value.__class__.__name__!r} ')

    return typing.cast(tp, value)
