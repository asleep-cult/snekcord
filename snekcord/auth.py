from __future__ import annotations

import enum
import re
import typing

if typing.TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    'AuthorizationType',
    'Authorization',
)

TOKEN_RE = re.compile(r'^((?P<prefix>Bot|Bearer) )?(?P<token>[\w.-]+)$')


class AuthorizationType(enum.Enum):
    BOT = 'Bot'
    BEARER = 'Bearer'
    USER = 'User'


class Authorization:
    def __init__(self, type: AuthorizationType, *, token: str) -> None:
        self.type = type
        self.token = token

    @classmethod
    def parse(cls, string: str) -> Self:
        match = TOKEN_RE.match(string)
        if match is None:
            raise ValueError(f'{string!r} is not a valid token')

        prefix = match.group('prefix')
        if prefix == 'Bot':
            type = AuthorizationType.BOT
        elif prefix == 'Bearer':
            type = AuthorizationType.BEARER
        else:
            type = AuthorizationType.USER

        return cls(type, token=match.group('token'))

    def to_token(self) -> str:
        if self.is_bot():
            return f'Bot {self.token}'
        elif self.is_bearer():
            return f'Bearer {self.token}'
        else:
            return self.token

    def __repr__(self) -> str:
        token = f'<{self.token[0:2]}...{self.token[-3:-1]}>'
        return f'Authorization(type={self.type!r}, token={token!r})'

    def is_bot(self) -> bool:
        return self.type is AuthorizationType.BOT

    def is_bearer(self) -> bool:
        return self.token is AuthorizationType.BEARER

    def is_user(self) -> bool:
        return self.token is AuthorizationType.USER

    def ws_connectable(self) -> bool:
        return self.is_bot() or self.is_user()
