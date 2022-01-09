from ..snowflake import Snowflake
from ..undefined import undefined

__all__ = ('JSONBuilder',)


def _transform_snowflake(value):
    return str(Snowflake(value))


class JSONBuilder(dict):
    """A class for building strongly typed JSON objects."""

    def set(self, key, value, *, nullable=False, transformer=None):
        if value is None:
            if not nullable:
                raise TypeError(f'{key!r} is not nullable')

            self[key] = value
        else:
            if value is undefined:
                return

            if transformer is not None:
                value = transformer(value)

            self[key] = value

    def set_array(self, key, values, *, nullable=False, transformer=None):
        if transformer is not None:
            transform = lambda values: [transformer(value) for value in values]
        else:
            transform = None

        return self.set(key, values, nullable=nullable, transformer=transform)

    def str(self, key, value, *, nullable=False):
        """Adds a string to the JSON object.

        Arguments:
            key (str): The key to place the string under.

            value (Optional[object]): The value to convert to a string.

            nullable (bool): Whether or not the string can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=str)

    def int(self, key, value, *, nullable=False):
        """Adds an integer to the JSON object.

        Arguments:
            key (str): The key to place the integer under.

            value (Optional[SupportsInt]): The value to convert to a integer.

            nullable (bool): Whether or not the integer can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=int)

    def float(self, key, value, *, nullable=False):
        """Adds a floating point number to the JSON object.

        Arguments:
            key (str): The key to place the floating point number under.

            value (Optional[SupportsFloat]): The value to convert to a floating point number.

            nullable (bool): Whether or not the floating point number can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=float)

    def bool(self, key, value, *, nullable=False):
        """Adds a boolean to the JSON object.

        Arguments:
            key (str): The key to place the boolean under.

            value (Optional[object]): The value to convert to a boolean.

            nullable (bool): Whether or not the boolean can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=bool)

    def snowflake(self, key, value, *, nullable=False):
        """Adds a snowflake to the JSON object.

        Arguments:
            key (str): The key to place the snowflake under.

            value (Optional[SupportsInt]): The value to convert to a snowflake.

            nullable (bool): Whether or not the snowflake can be None.

        Raises:
            TypeError: The value is not nullable but it was provided as None.
        """
        self.set(key, value, nullable=nullable, transformer=_transform_snowflake)

    def str_array(self, key, values, *, nullable=False):
        """Adds an array of strings to the JSON object.

        Arguments:
            key (str): The key to place the strings under.

            values (Optional[list[object]]): The values to convert to a strings.

            nullable (bool): Whether or not the strings can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=str)

    def int_array(self, key, values, *, nullable=False):
        """Adds an array of integers to the JSON object.

        Arguments:
            key (str): The key to place the integers under.

            values (Optional[list[SupportsInt]]): The values to convert to a integers.

            nullable (bool): Whether or not the integers can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=int)

    def float_array(self, key, values, *, nullable=False):
        """Adds an array of floating point numbers to the JSON object.

        Arguments:
            key (str): The key to place the floating point numbers under.

            values (Optional[list[SupportsFloat]]):
                The values to convert to a floating point numbers.

            nullable (bool): Whether or not the floating point numbers can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=float)

    def bool_array(self, key, values, *, nullable=False):
        """Adds an array of booleans to the JSON object.

        Arguments:
            key (str): The key to place the booleans under.

            values (Optional[list[object]]): The values to convert to a booleans.

            nullable (bool): Whether or not the booleans can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set_array(key, values, nullable=nullable, transformer=bool)

    def snowflake_array(self, key, values, *, nullable=False):
        """Adds an array of snowflakes to the JSON object.

        Arguments:
            key (str): The key to place the snowflakes under.

            values (Optional[list[SupportsInt]]): The values to convert to a snowflakes.

            nullable (bool): Whether or not the snowflakes can be None.

        Raises:
            TypeError: The values are not nullable but they were provided as None.
        """
        self.set(key, values, nullable=nullable, transformer=_transform_snowflake)
