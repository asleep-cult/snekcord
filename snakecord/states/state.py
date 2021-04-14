from __future__ import annotations


class BaseState:
    maxsize = 0

    @classmethod
    def set_maxsize(cls, maxsize: int) -> None:
        cls.maxsize = maxsize
