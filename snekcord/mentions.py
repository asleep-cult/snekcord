from collections.abc import Iterable

CHANNEL_MENTION = '<#{channel_id}>'
USER_MENTION = '<@{user_id}>'
ROLE_MENTION = '<@&{role_id}>'


class MessageMentions:
    __slots__ = ('roles', 'users', 'everyone', 'replied_user')

    def __init__(self, *, roles=False, users=False, everyone=False, replied_user=False):
        from .states import RoleState, UserState

        if isinstance(roles, Iterable):
            self.roles = set()
            for role in roles:
                self.roles.add(RoleState.unwrap_id(role))
        else:
            self.roles = bool(roles)

        if isinstance(users, Iterable):
            self.users = set()
            for user in users:
                self.users.add(UserState.unwrap_id(user))
        else:
            self.users = bool(users)

        self.everyone = bool(everyone)
        self.replied_user = bool(replied_user)

    def to_dict(self):
        data = {'parse': []}

        if isinstance(self.roles, set):
            data['roles'] = self.roles
        else:
            if self.roles is True:
                data['parse'].append('roles')

        if isinstance(self.users, set):
            data['users'] = self.users
        else:
            if self.users is True:
                data['parse'].append('users')

        if self.everyone is True:
            data['parse'].append('everyone')

        if self.replied_user is True:
            data['replied_user'] = True

        return data

    def __repr__(self):
        return (
            f'MessageMentions(roles={self.roles!r}, users={self.users!r}, '
            f'everyone={self.everyone!r}, replied_user={self.replied_user!r})'
        )


def mention_channel(channel):
    from .states import ChannelState

    channel_id = ChannelState.unwrap_id(channel)
    return CHANNEL_MENTION.format(channel_id=channel_id)


def mention_user(user):
    from .states import UserState

    user_id = UserState.unwrap_id(user)
    return USER_MENTION.format(user_id=user_id)


def mention_role(role):
    from .states import GuildRoleState

    role_id = GuildRoleState.unwrap_id(role)
    return ROLE_MENTION.format(role_id=role_id)
