from .channel import (
    TextChannel, 
    ChannelType,
    GuildChannel
)

from .utils import (
    JsonStructure,
    JsonField,
    JsonArray,
    Snowflake
)

from typing import (
    Union,
    Dict
)

class RoleTags(JsonStructure):
    bot_id: Snowflake = JsonField('bot_id', Snowflake, str)
    integration_id: Snowflake = JsonField('integration_id', Snowflake, str)
    premium_subscriber: bool = JsonField('premium_subscriber')

class Role(JsonStructure):
    id: Snowflake = JsonField('id', Snowflake, str)
    name: str = JsonField('name')
    color: int = JsonField('color')
    hoist: bool = JsonField('hoist')
    position: int = JsonField('position')
    permissions: str = JsonField('permissions')
    managed: bool = JsonField('managed')
    mentionable: bool = JsonField('mentionable')
    tags: RoleTags = JsonField('tags', struct=RoleTags)

class RoleState:
    def __init__(self, client, guild):
        self._client = client
        self._guild = guild
        self._roles = {}

    def get(self, item, default=None):
        try:
            snowflake = Snowflake(item)
        except (ValueError, TypeError):
            return default
        return self._roles.get(snowflake, default)

    def __getitem__(self, item):
        try:
            snowflake = Snowflake(item)
        except (ValueError, TypeError):
            snowflake = None
        return self._roles[snowflake]

    def __len__(self):
        return len(self._roles)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._roles)

    async def fetch(self, member_id):
        data = await self._client.rest.get_guild_role(self._guild.id, member_id)
        return self.add(data)

    def add(self, data):
        role = self.get(data['id'])
        if role is not None:
            role._update(data)
            return role
        role = Role.unmarshal(data, state=self, guild=self._guild)
        self._roles[role.id] = role
        return role

class GuildMember(JsonStructure):
    _user = JsonField('user')
    nick: str = JsonField('nick')
    _roles =  JsonField('roles')
    joined_at: str = JsonField('joined_at')
    premium_since: str = JsonField('premium_since')
    deaf: bool = JsonField('deaf')
    mute: bool = JsonField('mute')
    pending: bool = JsonField('pending')

    def __init__(self, *, state, guild, user=None):
        self._state = state
        self.guild = guild
        if user is not None:
            self._user = user
        else:
            self.user = state._client.users.add(self._user)

    @property
    def guilds(self):
        for guild in self._state._client.guilds:
            if self in guild.members:
                yield guild

    def _update(self, *args, **kwargs):
        pass

class GuildMemberState:
    def __init__(self, client, guild):
        self._client = client
        self._guild = guild
        self._members = {}

    def get(self, item, default=None):
        try:
            snowflake = Snowflake(item)
        except ValueError:
            return default
        return self._members.get(snowflake, default)

    def __getitem__(self, item):
        try:
            snowflake = Snowflake(item)
        except (ValueError, TypeError):
            snowflake = None
        return self._members[snowflake]

    def __len__(self):
        return len(self._members)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._members)

    async def fetch(self, member_id):
        data = await self._client.rest.get_guild_member(self._guild.id, member_id)
        return self.add(data)

    def add(self, data, user=None):
        if user is not None:
            member = self.get(user.id)
        else:
            member = self.get(data['user'].get('id'))
        if member is not None:
            member._update(data)
            return member
        member = GuildMember.unmarshal(data, state=self, guild=self._guild, user=user)
        self._members[member.user.id] = member
        return member

class Guild(JsonStructure):
    id: Snowflake = JsonField('id', Snowflake, str)
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
    venity_url_code: str = JsonField('vanity_url_code')
    premium_tier: int = JsonField('premium_tier')
    premium_subscription_count: int = JsonField('premium_subscription_count')
    system_channel_flags: int = JsonField('system_channel_flags')
    preferred_locale: str = JsonField('preferred_locale')
    rules_channel_id: Snowflake = JsonField('rules_channel_id', Snowflake, str)
    public_updates_channel_id: Snowflake = JsonField('public_updates_channel_id', Snowflake, str)
    emojis: list = JsonField('emojis')
    roles: list = JsonField('roles')
    _channels = JsonArray('channels')
    _members = JsonArray('members')
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

    def __eq__(self, other):
        return isinstance(other, Guild) and other.id == self.id

    def __str__(self):
        return self.name

    @property
    def channels(self):
        for channel in self._state._client.channels:
            if channel.guild == self:
                yield channel

class GuildState:
    def __init__(self, client):
        self._client = client
        self._guilds = {}

    def get(self, item, default=None):
        try:
            snowflake = Snowflake(item)
        except (ValueError, TypeError):
            return default
        return self._guilds.get(snowflake, default)

    def __getitem__(self, item):
        try:
            snowflake = Snowflake(item)
        except (ValueError, TypeError):
            snowflake = None
        return self._guilds[snowflake]

    def __len__(self):
        return len(self._guilds)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._guilds)

    async def fetch(self, guild_id):
        data = await self._client.rest.get_guild(guild_id)
        return self.add_channel(data)

    def add(self, data):
        guild = self.get(data['id'])
        if guild is not None:
            guild._update(data)
            return guild
        guild = Guild.unmarshal(data, state=self)
        self._guilds[guild.id] = guild
        return guild