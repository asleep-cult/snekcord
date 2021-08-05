from ..clients.client import ClientClasses
from ..enums import TeamMembershipState
from ..json import JsonField, JsonObject
from ..snowflake import Snowflake


class Team(JsonObject):
    id = JsonField('id', Snowflake)
    owner_id = JsonField('owner_user_id', Snowflake)

    def __init__(self, *, application):
        self.application = application
        self.members = {}

    @property
    def owner(self):
        return self.members.get(self.owner_id)

    def update(self, data):
        super().update(data)

        if 'members' in data:
            self.members.clear()

            for member in data['members']:
                member = ClientClasses.TeamMember.unmarshal(member, team=self)
                self.members[member.user.id] = member

        return self


class TeamMember(JsonObject):
    membership_state = JsonField('membership_state', TeamMembershipState.try_enum)
    team_id = JsonField('team_id', Snowflake)

    def __init__(self, *, team):
        self.team = team
        self.user = None

    def update(self, data):
        super().update(data)

        if 'user' in data:
            self.user = self.team.application.client.users.upsert(data['user'])

        return self
