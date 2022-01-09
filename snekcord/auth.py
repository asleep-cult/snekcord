import enum
import re

TOKEN_RE = re.compile(r'^((?P<prefix>Bot|Bearer) )?(?P<token>[\w.-]+)$')


class AuthorizationType(enum.Enum):
    BOT = 'Bot'
    BEARER = 'Bearer'
    USER = 'User'


class Authorization:
    def __init__(self, type, *, token):
        self.type = type
        self.token = token

    @classmethod
    def parse(cls, string):
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

    def to_token(self):
        if self.is_bot():
            return f'Bot {self.token}'
        elif self.is_bearer():
            return f'Bearer {self.token}'
        else:
            return self.token

    def __repr__(self):
        token = f'<{self.token[0:2]}...{self.token[-3:-1]}>'
        return f'Authorization(type={self.type!r}, token={token!r})'

    def is_bot(self):
        return self.type is AuthorizationType.BOT

    def is_bearer(self):
        return self.token is AuthorizationType.BEARER

    def is_user(self):
        return self.token is AuthorizationType.USER

    def ws_connectable(self):
        return self.is_bot() or self.is_user()
