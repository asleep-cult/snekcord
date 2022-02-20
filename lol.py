import typing


def f() -> typing.Union[int, str]:
    ...


x: int = f()
reveal_type(x)
