from datetime import datetime

from .snowflake import Snowflake

__all__ = ('TOKEN_EPOCH', 'get_token_type', 'strip_token_type', 'split_token',
           'get_token_id', 'get_token_timestamp', 'get_token_time',
           'get_token_hmac')

TOKEN_EPOCH: int


def get_token_type(token: str) -> str: ...


def strip_token_type(token: str) -> str: ...


def split_token(token: str) -> list[str]: ...


def get_token_id(token: str) -> Snowflake: ...


def get_token_timestamp(token: str) -> int: ...


def get_token_time(token: str) -> datetime: ...


def get_token_hmac(token: str) -> bytes: ...
