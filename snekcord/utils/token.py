from base64 import b64decode
from datetime import datetime

from . import Snowflake

__all__ = ('TOKEN_EPOCH', 'get_token_type', 'strip_token_type', 'split_token',
           'get_token_id', 'get_token_timestamp', 'get_token_time',
           'get_token_hmac')

TOKEN_EPOCH = 1293840000


def _padded(string):
    return string + '=' * (4 - len(string) % 4)


def get_token_type(token):
    return token.strip().split()[0].strip()


def strip_token_type(token):
    if ' ' not in token:
        return token
    return ' '.join(token.strip().split()[1:])


def split_token(token):
    parts = strip_token_type(token).split('.', 2)
    if len(parts) != 3:
        raise ValueError('Invalid Token')
    return parts


def get_token_id(token):
    part = _padded(split_token(token)[0])
    return Snowflake(b64decode(part))


def get_token_timestamp(token):
    part = _padded(split_token(token)[1])
    timestamp = int.from_bytes(b64decode(part), 'big', signed=False)
    if timestamp < TOKEN_EPOCH:
        # If the timestamp is less than TOKEN_EPOCH then
        # it represents the time the token was generated (I think?)
        # otherwise this timestamp represents the time the application
        # was created.
        timestamp += TOKEN_EPOCH
    return timestamp


def get_token_time(token):
    return datetime.fromtimestamp(get_token_timestamp(token))


def get_token_hmac(token):
    part = _padded(split_token(token)[2])
    return b64decode(part)
