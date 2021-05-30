from base64 import urlsafe_b64decode
from datetime import datetime

from . import Snowflake

__all__ = ('Token',)


def _padded(string):
    return string + '=' * (4 - len(string) % 4)


class Token(str):
    __slots__ = ('parts',)

    TOKEN_EPOCH = 1293840000

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.parts = tuple(self.split('.', 2))
        return self

    @property
    def id(self):
        decoded = urlsafe_b64decode(_padded(self.parts[0]))
        return Snowflake(decoded.decode())

    @property
    def timestamp(self):
        decoded = urlsafe_b64decode(_padded(self.parts[1]))
        return (self.TOKEN_EPOCH
                + int.from_bytes(decoded, 'little', signed=False))

    @property
    def time(self):
        return datetime.fromtimestamp(self.timestamp)

    @property
    def hmac(self):
        # I don't know if this is right... ?
        return urlsafe_b64decode(_padded(self.parts[2]))
