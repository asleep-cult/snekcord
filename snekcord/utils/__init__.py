from .events import *
from .json import *
from .snowflake import *
from .token import *
from .undefined import *


def _validate_keys(name, source, required, keys):
    for key in required:
        if key not in source:
            raise ValueError(f'{name} is missing required key {key!r}')

    for key in source:
        if key not in keys:
            raise ValueError(f'{name} received an unexpected key {key!r}')
