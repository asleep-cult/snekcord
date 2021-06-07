import typing as t

from .aitertools import *
from .bitset import *
from .enum import *
from .events import *
from .json import *
from .permissions import *
from .snowflake import *
from .token import *
from .undefined import *


def _validate_keys(name: str, source: t.Iterable[str],  # type: ignore
                   required: t.Iterable[str], keys: t.Iterable[str]) -> None:
    for key in required:
        if key not in source:
            raise ValueError(f'{name} is missing required key {key!r}')

    for key in source:
        if key not in keys:
            raise ValueError(f'{name} received an unexpected key {key!r}')
