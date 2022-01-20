import enum


class FetchOrdering(str, enum.Enum):
    BEFORE = 'before'
    AFTER = 'after'
    AROUND = 'around'
