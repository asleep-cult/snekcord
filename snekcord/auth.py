import enum
import re

TOKEN_RE = re.compile(r'^((?P<prefix>Bot|Bearer) )?(?P<token>[\w.-]+)$')


class AuthorizationType(enum.Enum):
    Bot = 0
    Bearer = 1
    User = 2


class Authorization:
    def __init__(self, type, token):
        self.token = token
        self.type = type

    def __repr__(self):
        return f'<{self.__class__.__name__} type={self.type.name}>'

    @classmethod
    def from_string(cls, string):
        match = TOKEN_RE.match(string)

        if match is None:
            raise ValueError(f'{string!r} is not a valid token')

        prefix = match.group('prefix')

        if prefix == 'Bot':
            type = AuthorizationType.Bot
        elif prefix == 'Bearer':
            type = AuthorizationType.Bearer
        else:
            type = AuthorizationType.User

        return cls(type, match.group('token'))

    def to_string(self):
        if self.is_bot():
            return f'Bot {self.token}'
        elif self.is_bearer():
            return f'Bearer {self.token}'
        else:
            return self.token

    def is_bot(self):
        return self.type == AuthorizationType.Bot

    def is_bearer(self):
        return self.type == AuthorizationType.Bearer

    def is_user(self):
        return self.type == AuthorizationType.User

    def is_mfa(self):
        return self.is_user() and self.token.startswith('mfa.')

    def gateway_allowed(self):
        return self.type in (AuthorizationType.Bot, AuthorizationType.User)
