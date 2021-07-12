import enum
import re

TOKEN_RE = re.compile(r'^((?P<prefix>Bot|Bearer) )?(?P<token>[\w.-]+)$')


class AuthorizationType(enum.Enum):
    BOT = 'Bot'
    BEARER = 'Bearer'
    USER = 'User'


class Authorization:
    def __init__(self, type, token):
        self.token = token
        self.type = type

    def __repr__(self):
        return f'<{self.__class__.__name__} type={self.type!r}>'

    @classmethod
    def from_string(cls, string):
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

        return cls(type, match.group('token'))

    def to_string(self):
        if self.is_bot():
            return f'Bot {self.token}'
        elif self.is_bearer():
            return f'Bearer {self.token}'
        else:
            return self.token

    def is_bot(self):
        return self.type == AuthorizationType.BOT

    def is_bearer(self):
        return self.type == AuthorizationType.BEARER

    def is_user(self):
        return self.type == AuthorizationType.USER

    def is_mfa(self):
        return self.is_user() and self.token.startswith('mfa.')

    def gateway_allowed(self):
        return self.type in (AuthorizationType.BOT, AuthorizationType.USER)
