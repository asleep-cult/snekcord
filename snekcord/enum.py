import typing

__all__ = ('convert_enum',)

EnumT = typing.TypeVar('EnumT')
ValueT = typing.TypeVar('ValueT')


def convert_enum(enum: typing.Type[EnumT], value: ValueT) -> typing.Union[EnumT, ValueT]:
    try:
        return enum(value)
    except ValueError:
        return value
