import typing

from ..objects import CodeWrapper, Invite

__all__ = ('SupportsInviteCode', 'InviteCodeWrapper')

SupportsInviteCode = typing.Union[str, Invite]
InviteCodeWrapper = CodeWrapper[SupportsInviteCode, Invite]
