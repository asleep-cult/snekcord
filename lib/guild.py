from .user import User
from .invite import GuildInviteState

from .channel import (
    _Channel,
    ChannelState
)

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

from typing import Iterable


# TODO: Add GuildPreview, add IntegrationState, add Integration, add Widget

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

    def __init__(self, state, guild):
        self._state = state
        self.guild = guild

    async def edit(
        self,
        *,
        name=None,
        permissions=None,
        color=None,
        hoist=None,
        mentionable=None
    ):
        rest = self._state._client.rest
        resp = await rest.modify_guild_role(
            self.guild.id, self.id, name=name, 
            permission=permissions, color=color, 
            hoist=hoist, mentionable=mentionable
        )
        data = await resp.json()
        role = self._add(data)
        return role
    
    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_guild_role(
            self.guild.id, self.id
        )


class RoleState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data):
        role = self.get(data['id'])
        if role is not None:
            role._update(data)
            return role
        role = Role.unmarshal(data, state=self, guild=self._guild)
        self._values[role.id] = role
        return role

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_guild_roles(self._guild.id)
        data = await resp.json()
        roles = []
        for role in roles:
            role = self._add(role)
            roles.append(role)
        return roles

    async def create(
        self,
        *,
        name=None,
        permissions=None,
        color=None,
        hoist=None,
        mentionable=None
    ):
        rest = self._client.rest
        resp = await rest.create_guild_role(
            self._guild.id, name=name, permission=permissions,
            color=color, hoist=hoist, mentionable=mentionable
        )
        data = await resp.json()
        role = self._add(data)
        return role

    async def modify_postions(self, positions):
        rest = self._client.rest
        resp = await rest.modify_guild_role_permissions(self._guild.id, positions)
        data = await resp.json()
        roles = []
        for role in data:
            role = self._add(role)
            roles.append(role)
        return roles


class GuildMember(User):
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

    def __init__(self, *, state: 'GuildMemberState', guild: 'Guild', user=None):
        self._state: GuildMemberState = state
        self.guild = guild
        self.roles = GuildMemberRoleState(self._state._client, member=self)

        if self._roles is not None:
            for role in self._roles:
                self.roles._add(role)

        if user is not None:
            self.user = user
        else:
            self.user = self._state._client.users._add(self._user)

        del self._user
        del self._roles

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

    async def edit(self, nick=None, roles=None, mute=None, deaf=None, channel=None):
        rest = self._client.rest

        if channel is not None:
            channel = channel.id

        resp = await rest.modify_guild_member(
            self.guild.id, self.id, roles=roles, 
            mute=mute, deaf=deaf, channel=channel
        )
        data = await resp.json()
        member = self._add(data)
        return member


class GuildMemberRoleState(BaseState):
    def __init__(self, client, member):
        super().__init__(client)
        self._member = member

    def _add(self, role):
        if isinstance(role, Role):
            self._values[role.id] = role
            return role
        role = self._member.guild.roles.get(role)
        if role is not None:
            self._values[role.id] = role
        return role

    async def add(self, role):
        rest = self._client.rest
        await rest.add_guild_member_role(self._member.guild.id, self._member.id, role.id)

    async def remove(self, role):
        rest = self._client.rest
        await rest.remove_guild_member_role(self._member.guild.id, self._member.id, role.id)


class GuildMemberState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data, user=None):
        if user is None:
            user = self._client.users._add(data['user'])
        member = self.get(user.id)
        if member is not None:
            member._update(data)
            return member
        member = GuildMember.unmarshal(data, state=self, guild=self._guild, user=user)
        self._values[member.id] = member
        return member

    async def fetch(self, member_id):
        rest = self._client.rest
        data = await rest.get_guild_member(self._guild.id, member_id)
        member = self._add(data)
        return member

    async def fetch_many(self, limit=1000, before=None):
        rest = self._client.rest
        resp = await rest.get_guild_members(self._guild.id, limit, before)
        data = await resp.json()
        members = []
        for member in members:
            member = self._add(member)
            members.append(member)
        return members

    async def add(self, user, access_token, *, nick=None, roles=None, mute=None, deaf=None):
        rest = self._client.rest
        if roles is not None:
            roles = {role.id for role in roles}
        resp = await rest.add_guild_member(
            self._guild.id, user.id, access_token,
            nick=nick, roles=roles, mute=mute,
            deaf=deaf
        )
        data = await resp.json()
        member = self._add(data, user=user)
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

    def __init__(self, *, state: 'GuildState'):
        self._state = state
        self.roles: Iterable[Role] = RoleState(self._state._client, guild=self)
        self.members: Iterable[GuildMember] = GuildMemberState(self._state._client, guild=self)
        self.invites = GuildInviteState(self._state._client.invites, guild=self)
        self.bans = GuildBanState(self._state._client, guild=self)

        shard_id = ((self.id >> 22) % len(self._state._client.ws.shards))
        self.shard = self._state._client.ws.shards.get(shard_id)

        for channel in self._channels:
            self._state._client.channels._add(channel)

        for member in self._members:
            self.members._add(member)

        del self._channels
        del self._members

    def to_dict(self):
        dct = super().to_dict()
        members = dct['members'] = []
        channels = dct['channels'] = []
        for member in self.members:
            members.append(member.to_dict())
        for channel in self.channels:
            channels.append(channel.to_dict())
        return dct

    async def fetch_preview(self):
        rest = self._state._client.rest
        resp = await rest.get_guild_preview(self.id)
        data = await resp.json()

    async def edit(
        self,
        *,
        name=None, 
        region=None,
        verification_level=None, 
        default_message_notifications=None,
        explicit_content_filter=None,
        afk_channel=None,
        afk_timeout=None,
        icon=None,
        owner=None,
        splash=None,
        banner=None,
        system_channel=None,
        rules_channel=None,
        public_updates_channel=None,
        preferred_locale=None
    ):
        rest = self._state._client.rest

        if afk_channel is not None:
            afk_channel = afk_channel.id

        if owner is not None:
            owner = owner.id

        if system_channel is not None:
            system_channel = system_channel.id

        if rules_channel is not None:
            rules_channel = rules_channel.id

        if public_updates_channel is not None:
            public_updates_channel = public_updates_channel.id

        await rest.modify_guild(
            name=name, region=region,
            verification_level=verification_level,
            default_message_notifications=default_message_notifications,
            explicit_content_filter=explicit_content_filter,
            afk_channel_id=afk_channel, afk_timeout=afk_timeout,
            icon=icon, owner_id=owner, splash=splash,
            banner=banner, system_channel_id=system_channel,
            rules_channel_id=rules_channel, 
            public_updates_channel_id=public_updates_channel,
            preferred_locale=preferred_locale
        )

    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_guild(self.id)

    async def fetch_voice_region(self):
        rest = self._state._client.rest
        resp = await rest.get_guild_voice_region(self.id)
        data = await resp.json()
        return data

    async def fetch_vanity_url(self):
        rest = self._state._client.rest
        resp = await rest.get_guild_vanity_url(self.id)
        data = await resp.json()
        return data


class GuildBan(JsonStructure):
    reason = JsonField('reason')
    _user = JsonField('user')

    def __init__(self, state):
        self._state = state
        self.user = state._client._users.add(self._user)

        del self._user


class GuildBanState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data):
        ban = self.get(data['user']['id'])
        if ban is not None:
            ban._update(data)
            return ban
        ban = GuildBan.unmarshal(data, state=self)
        self._values[ban.user.id] = ban
        return ban

    async def fetch(self, user):
        rest = self._client.rest
        resp = await rest.get_guild_ban(self._guild.id, user.id)
        data = await resp.json()
        ban = self._add(data)
        return ban

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_guild_bans(self._guild.id)
        data = await resp.json()
        bans = []
        for ban in data:
            ban = self._add(data)
            bans.append(ban)
        return bans

    async def add(self, user, *, delete_message_days=None, reason=None):
        rest = self._client.rest
        await rest.create_guild_ban(self._guild.id, user.id, delete_message_days, reason)

    async def remove(self, user):
        rest = self._client.rest
        await rest.remove_guild_ban(self._guild.id, user.id)

class GuildState(BaseState):
    def _add(self, data) -> Guild:
        guild = self.get(data['id'])
        if guild is not None:
            guild._update(data)
            return guild
        guild = Guild.unmarshal(data, state=self)
        self._values[guild.id] = guild
        return guild

    async def fetch(self, guild_id) -> Guild:
        data = await self._client.rest.get_guild(guild_id)
        return self._add(data)