import builtins
import typing

from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

__all__ = (
    'JSONStr',
    'JSONInt',
    'JSONFloat',
    'JSONBool',
    'JSONSnowflake',
    'JSONStrArray',
    'JSONIntArray',
    'JSONFloatArray',
    'JSONBoolArray',
    'JSONSnowflakeArray',
    'JSONBuilder',
)

T = typing.TypeVar('T')

JSONStr = MaybeUndefined[typing.Any]
JSONInt = MaybeUndefined[typing.SupportsInt]
JSONFloat = MaybeUndefined[typing.SupportsFloat]
JSONBool = MaybeUndefined[typing.Any]
JSONSnowflake = MaybeUndefined[typing.SupportsInt]

JSONStrArray = MaybeUndefined[typing.Iterable[typing.Any]]
JSONIntArray = MaybeUndefined[typing.Iterable[typing.SupportsInt]]
JSONFloatArray = MaybeUndefined[typing.Iterable[typing.SupportsFloat]]
JSONBoolArray = MaybeUndefined[typing.Iterable[typing.Any]]
JSONSnowflakeArray = MaybeUndefined[typing.Iterable[typing.SupportsInt]]


def _transform_snowflake(value: typing.SupportsInt) -> str:
    return str(Snowflake(value))


class JSONBuilder(typing.Dict[str, typing.Any]):
    """A class for building strongly typed JSON objects."""

    def set(
        self,
        key: builtins.str,
        value: MaybeUndefined[typing.Optional[T]],
        *,
        nullable: builtins.bool = False,
        transformer: typing.Optional[typing.Callable[[T], typing.Any]] = None,
    ) -> None:
        if value is None:
            if not nullable:
                raise TypeError(f'{key!r} is not nullable')

            self[key] = value
        else:
            if value is not undefined:
                self[key] = transformer(value) if transformer is not None else value

    def set_array(
        self,
        key: builtins.str,
        values: MaybeUndefined[typing.Optional[typing.Iterable[T]]],
        *,
        nullable: builtins.bool = False,
        transformer: typing.Optional[typing.Callable[[T], typing.Any]] = None,
    ) -> None:
        if transformer is not None:
            transform = transformer
            self.set(
                key,
                values,
                nullable=nullable,
                transformer=lambda values: [transform(value) for value in values],
            )
        else:
            self.set(key, values, nullable=nullable)

    def str(
        self,
        key: builtins.str,
        value: typing.Optional[JSONStr],
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds a string to the JSON object.

        Arguments:
            key (str): The key to place the string under.

            value (JSONStr): The value to convert to a string.

            nullable (bool): Whether or not the string can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=str)

    def int(
        self, key: builtins.str, value: typing.Optional[JSONInt], *, nullable: builtins.bool = False
    ) -> None:
        """Adds an integer to the JSON object.

        Arguments:
            key (str): The key to place the integer under.

            value (JSONInt): The value to convert to a integer.

            nullable (bool): Whether or not the integer can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=int)

    def float(
        self,
        key: builtins.str,
        value: typing.Optional[JSONFloat],
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds a floating point number to the JSON object.

        Arguments:
            key (str): The key to place the floating point number under.

            value (JSONFloat): The value to convert to a floating point number.

            nullable (bool): Whether or not the floating point number can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=float)

    def bool(
        self,
        key: builtins.str,
        value: typing.Optional[JSONBool],
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds a boolean to the JSON object.

        Arguments:
            key (str): The key to place the boolean under.

            value (JSONBool): The value to convert to a boolean.

            nullable (bool): Whether or not the boolean can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=bool)

    def snowflake(
        self,
        key: builtins.str,
        value: typing.Optional[JSONSnowflake],
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds a snowflake to the JSON object.

        Arguments:
            key (str): The key to place the snowflake under.

            value (JSONSnowflake): The value to convert to a snowflake.

            nullable (bool): Whether or not the snowflake can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=_transform_snowflake)

    def str_array(
        self,
        key: builtins.str,
        values: typing.Optional[JSONStrArray],
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds an array of strings to the JSON object.

        Arguments:
            key (str): The key to place the strings under.

            values (JSONStrArray): The values to convert to a strings.

            nullable (bool): Whether or not the strings can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=str)

    def int_array(
        self,
        key: builtins.str,
        values: JSONIntArray,
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds an array of integers to the JSON object.

        Arguments:
            key (str): The key to place the integers under.

            values (JSONIntArray): The values to convert to a integers.

            nullable (bool): Whether or not the integers can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=int)

    def float_array(
        self,
        key: builtins.str,
        values: JSONFloatArray,
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds an array of floating point numbers to the JSON object.

        Arguments:
            key (str): The key to place the floating point numbers under.

            values (JSONFloatArray): The values to convert to a floating point numbers.

            nullable (bool): Whether or not the floating point numbers can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=float)

    def bool_array(
        self,
        key: builtins.str,
        values: JSONBoolArray,
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds an array of booleans to the JSON object.

        Arguments:
            key (str): The key to place the booleans under.

            values (JSONBoolArray): The values to convert to a booleans.

            nullable (bool): Whether or not the booleans can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=bool)

    def snowflake_array(
        self,
        key: builtins.str,
        values: JSONSnowflakeArray,
        *,
        nullable: builtins.bool = False,
    ) -> None:
        """Adds an array of snowflakes to the JSON object.

        Arguments:
            key (str): The key to place the snowflakes under.

            values (JSONSnowflakeArray): The values to convert to a snowflakes.

            nullable (bool): Whether or not the snowflakes can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=_transform_snowflake)
