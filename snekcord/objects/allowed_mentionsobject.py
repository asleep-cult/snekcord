from ..utils import (
    JsonArray, JsonField, JsonObject, JsonTemplate, Snowflake
)

AllowedMentionsTemplate = JsonTemplate(
    parse=JsonArray('parse'),
    roles=JsonArray('roles', Snowflake.try_snowflake, str),
    users=JsonArray('users', Snowflake.try_snowflake, str),
    replied_user=JsonField('replied_user')
)

class AllowedMentions(JsonObject, template=AllowedMentionsTemplate):
    def __init__(self, users = None, roles = None, replied_users = False):
        if users is not None:
            if isinstance(users, bool):
                users = users
            elif isinstance(users, list):
                users = [Snowflake.try_snowflake(user) for user in users]
            else:
                raise TypeError(f'users must be a bool, list or None, not {users.__class__.__name__}')

        if roles is not None:
            if isinstance(roles, bool):
                roles = roles
            elif isinstance(users, list):
                roles = [Snowflake.try_snowflake(role) for role in roles]
            else:
                raise TypeError(f'roles must be a bool, list or None, not {roles.__class__.__name__}')
        
        self.users = users
        self.roles = roles
        self.replied_users = replied_users
