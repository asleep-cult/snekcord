import enum
import typing


class FruitType(enum.Enum):
    APPLE = enum.auto()
    BANANA = enum.auto()


@typing.final
class Apple:
    type: typing.Literal[FruitType.APPLE]


@typing.final
class Banana:
    type: typing.Literal[FruitType.BANANA]


Fruit = typing.Union[Apple, Banana]


def eat_fruit(fruit: Fruit) -> None:
    fruit_type = fruit.type

    if fruit_type is FruitType.APPLE:
        reveal_type(fruit)
