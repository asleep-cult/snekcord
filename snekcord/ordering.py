import enum

__all__ = ('FetchOrdering',)


class FetchOrdering(str, enum.Enum):
    BEFORE = 'before'
    AFTER = 'after'
    AROUND = 'around'
