from .bases import (
    BaseObject, 
    BaseState
)

from .utils import (
    JsonStructure,
    JsonField,
    JsonArray,
    Snowflake,
)


class RoleTags(JsonStructure):
    __json_slots__ = ('bot_id', 'integration_id', 'premium_subscriber')

    bot_id: Snowflake = JsonField('bot_id', Snowflake, str)
    integration_id: Snowflake = JsonField('integration_id', Snowflake, str)
    premium_subscriber: bool = JsonField('premium_subscriber')


class Role(BaseObject):
    __json_slots__ = ('id', 'name', 'color', 'hoist', 'position', 'permissions', 'managed', 'mentionable', 'tags')

    name: str = JsonField('name')
    color: int = JsonField('color')
    hoist: bool = JsonField('hoist')
    position: int = JsonField('position')
    permissions: str = JsonField('permissions')
    managed: bool = JsonField('managed')
    mentionable: bool = JsonField('mentionable')
    tags: RoleTags = JsonField('tags', struct=RoleTags)


class RoleState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    async def fetch(self, member_id):
        data = await self._client.rest.get_guild_role(self._guild.id, member_id)
        return self.add(data)

    def add(self, data):
        role = self.get(data['id'])
        if role is not None:
            role._update(data)
            return role
        role = Role.unmarshal(data, state=self, guild=self._guild)
        self._values[role.id] = role
        return role


class GuildMember(BaseObject):
    __json_slots__ = (
        '_user', 'nick', '_roles', 'joined_at', 'premium_since', 'deaf', 'mute', 
        'pending', '_state', 'guild', 'user'
    )

    json_fields = {}
    _user = JsonField('user')
    nick: str = JsonField('nick')
    _roles = JsonField('roles')
    joined_at: str = JsonField('joined_at')
    premium_since: str = JsonField('premium_since')
    deaf: bool = JsonField('deaf')
    mute: bool = JsonField('mute')
    pending: bool = JsonField('pending')

    def __init__(self, *, state, guild, user=None):
        self._state = state
        self.guild = guild
        if user is not None:
            self.user = user
        else:
            self.user = state._client.users.add(self._user)

    @property
    def guilds(self):
        for guild in self._state._client.guilds:
            if self in guild.members:
                yield guild

    def __getattribute__(self, name):
        try:
            attr = super().__getattribute__(name)
        except AttributeError as e:
            try:
                attr = self.user.__getattribute__(name)
            except AttributeError:
                raise e
        return attr

    def _update(self, *args, **kwargs):
        pass


class GuildMemberState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    async def fetch(self, member_id):
        data = await self._client.rest.get_guild_member(self._guild.id, member_id)
        return self.add(data)

    def add(self, data, user=None):
        if user is None:
            user = self._client.users.add(data['user'])
        member = self.get(user.id)
        if member is not None:
            member._update(data)
            return member
        member = GuildMember.unmarshal(data, state=self, guild=self._guild, user=user)
        self._values[member.id] = member
        return member


class Guild(BaseObject):
    __json_slots__ = (
        '_state', 'members', 'shard', 'name', 'description', 
        'owner_id', 'region', 'features', 'afk_channel_id', 
        'afk_timeout', 'system_channel_id', 'verification_level', 
        'widget_enabled', 'widget_channel_id', 'default_message_notifications', 
        'mfa_level', 'explicit_content_filter', 'max_presences', 'max_members', 
        'max_video_channel_users', 'vanity_url_code', 'premium_tier', 
        'premium_subscription_count', 'system_channel_flags', 'preferred_locale',
        'rules_channel_id', 'public_updates_channel_id', 'emojis', 'roles', '_channels', 
        '_members', 'member_count', 'presence_count', 'id'
    )

    name: str = JsonField('name')
    description: str = JsonField('description')
    owner_id: Snowflake = JsonField('owner_id', Snowflake, str)
    region: str = JsonField('region')
    features: tuple = JsonField('features', tuple)
    afk_channel_id: Snowflake = JsonField('afk_channel_id', Snowflake, str)
    afk_timeout: float = JsonField('afk_timeout', float)
    system_channel_id: Snowflake = JsonField('system_channel_id', Snowflake, str)
    verification_level: int = JsonField('verification_level')
    widget_enabled: bool = JsonField('widget_enabled')
    widget_channel_id: Snowflake = JsonField('widget_channel_id', Snowflake, str)
    default_message_notifications: int = JsonField('default_message_notifications')
    mfa_level: int = JsonField('mfa_level')
    explicit_content_filter: int = JsonField('explicit_content_filter')
    max_presences: int = JsonField('max_presences')
    max_members: int = JsonField('max_members')
    max_video_channel_users: int = JsonField('max_video_channel_users')
    vanity_url_code: str = JsonField('vanity_url_code')
    premium_tier: int = JsonField('premium_tier')
    premium_subscription_count: int = JsonField('premium_subscription_count')
    system_channel_flags: int = JsonField('system_channel_flags')
    preferred_locale: str = JsonField('preferred_locale')
    rules_channel_id: Snowflake = JsonField('rules_channel_id', Snowflake, str)
    public_updates_channel_id: Snowflake = JsonField('public_updates_channel_id', Snowflake, str)
    emojis: list = JsonField('emojis')
    roles: RoleState = JsonField('roles')
    _channels: list = JsonArray('channels')
    _members: list = JsonArray('members')
    member_count: int = JsonField('approximate_member_count')
    presence_count: int = JsonField('approximate_presence_count')

    def __init__(self, *, state):
        self._state = state
        self.roles = RoleState(state._client, guild=self)
        self.members = GuildMemberState(state._client, guild=self)

        shard_id = ((self.id >> 22) % len(state._client.ws.shards))
        self.shard = state._client.ws.shards.get(shard_id)

        for channel in self._channels:
            state._client.channels.add(channel, guild=self)

        for member in self._members:
            self.members.add(member)

        del self._channels
        del self._members

    @property
    def channels(self):
        for channel in self._state._client.channels:
            if channel.guild == self:
                yield channel


class GuildState(BaseState):
    async def fetch(self, guild_id):
        data = await self._client.rest.get_guild(guild_id)
        return self.add(data)

    def add(self, data):
        guild = self.get(data['id'])
        if guild is not None:
            guild._update(data)
            return guild
        guild = Guild.unmarshal(data, state=self)
        self._values[guild.id] = guild
        return guild