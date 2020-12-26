from .user import User
from .invite import GuildInviteState

from .channel import (
    _Channel,
    GuildChannelState
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
        role = self._state._add(data)
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
        for role in data:
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
    _roles: list = JsonField('roles')
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

    async def ban(self, *, reason=None, delete_message_days=None):
        ban = await self._guild.bans.add(self, reason=reason, delete_message_days=delete_message_days)
        return ban


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
        for member in data:
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


class GuildEmoji(BaseObject):
    name = JsonField('name')
    _roles = JsonArray('roles')
    _user = JsonField('user')
    required_colons = JsonField('required_colons')
    managed = JsonField('managed')
    animated = JsonField('animated')
    available = JsonField('available')

    def __init__(self, state, guild):
        self._state = state
        self.guild = guild
        self.roles = []
        self.user = None
        
        if self._user is not None:
            self.user = self._state._client.users._add(self._user)

        for role in self._roles:
            role = self.guild.roles.get(role)
            if role is not None:
                self.roles.append(role)

        del self._roles
        del self._user

    def __str__(self):
        if self.id is None:
            return self.name
        elif self.animated:
            return '<a:%s:%s>' % (self.name, self.id)
        else:
            return '<:%s:%s>' % (self.name, self.id)

    def __repr__(self):
        return '<String: %r, Roles: %s, Guild: %s>' % (
            str(self), self.roles, self.guild)

    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_guild_emoji(self.guild.id, self.id)

    async def edit(self, name=None, roles=None):
        rest = self._state._client.rest
        await rest.modify_guild_emoji(self.guild.id, self.id, name, roles)

    def to_dict(self):
        dct = super().to_dict()

        if self.user is not None:
            dct['user'] = self.user.to_dict()

        dct['roles'] = [role.id for role in self.roles]

        return dct


class GuildEmojiState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data):
        emoji = self.get(data.get('id'))
        if emoji is not None:
            emoji._update(data)
            return emoji
        emoji = GuildEmoji.unmarshal(data, state=self, guild=self._guild)
        self._values[emoji.id] = emoji
        return emoji

    async def fetch(self, emoji_id):
        rest = self._client.rest
        resp = await rest.get_guild_emoji(self._guild.id, emoji_id)
        data = await resp.data()
        emoji = self._add(data)
        return emoji

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_guild_emojis(self._guild.id)
        data = await resp.data()
        emojis = []
        for emoji in data:
            emoji = self._add(emoji)
            emojis.append(emoji)
        return emojis

    async def create(self, name, image, roles=None):
        rest = self._client.rest
        resp = await rest.create_guild_emoji(self._guild.id, name, image, roles)
        data = await resp.json()
        emoji = self._add(data)
        return emoji


class GuildPreview(BaseObject):
    # Basically a partial guild?
    name = JsonField('name')
    icon = JsonField('icon')
    splash = JsonField('splash')
    discovery_splash = JsonField('discovery_splash')
    _emojis = JsonArray('emojis')
    features = JsonArray('features')
    member_count = JsonField('approximate_member_count')
    presence_count = JsonField('approximate_presence_count')
    description = JsonField('description')

    def __init__(self, state):
        self._state = state
        self.emojis = GuildEmojiState(self._state._client, guild=self)
        self.roles: Iterable[Role] = RoleState(self._state._client, guild=self)
        self.members: Iterable[GuildMember] = GuildMemberState(self._state._client, guild=self)
        self.invites = GuildInviteState(self._state._client.invites, guild=self)
        self.bans = GuildBanState(self._state._client, guild=self)
        self.channels = GuildChannelState(self._state._client.channels, guild=self)

        for emoji in self._emojis:
            self.emojis._add(emoji)

        del self._emojis

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

    def to_dict(self, cls=None):
        dct = super().to_dict(cls=cls)

        emojis = []
        for emoji in self.emojis:
            emojis.append(emoji.to_dict())

        dct['emojis'] = emojis
    
        return dct


class Guild(GuildPreview):
    icon_hash = JsonField('icon_hash')
    _owner = JsonField('owner')
    owner_id = JsonField('owner_id', Snowflake, str)
    permissions = JsonField('permissions')
    region = JsonField('region')
    afk_channel_id = JsonField('afk_channel_id', Snowflake, str)
    afk_timeout = JsonField('afk_timeout')
    widget_enabled = JsonField('widget_enabled')
    widget_channel_id = JsonField('widget_channel_id', Snowflake, str)
    verification_level = JsonField('verification_level')
    default_message_notifications = JsonField('default_message_notifications')
    explicit_content_filter = JsonField('explicit_content_filter')
    _roles = JsonArray('roles')
    mfa_level = JsonField('mfa_level')
    application_id = JsonField('application_id', Snowflake, str)
    system_channel_id = JsonField('system_channel_id', Snowflake, str)
    system_channel_flags = JsonField('system_channel_flags')
    rules_channel_id = JsonField('rules_channel_id', Snowflake, str)
    joined_at = JsonField('joined_at')
    large = JsonField('large')
    unavailable = JsonField('unavailable')
    member_count = JsonField('member_count')
    _voice_states = JsonArray('voice_states')
    _members = JsonArray('members')
    _channels = JsonArray('channels')
    _presences = JsonArray('presences')
    max_presences = JsonField('max_presences')
    max_members = JsonField('max_members')
    vanity_url_code = JsonField('vanity_url_code')
    banner = JsonField('banner')
    premium_tier = JsonField('permium_tier')
    premium_subscription_count = JsonField('premium_subscription_count')
    preferred_locale = JsonField('preferred_locale')
    public_updates_channel_id = JsonField('public_updates_channel_id', Snowflake, str)
    max_video_channel_users = JsonField('max_video_channel_users')

    def __init__(self, *, state: 'GuildState'):
        super().__init__(state)

        shard_id = ((self.id >> 22) % len(self._state._client.ws.shards))
        self.shard = self._state._client.ws.shards.get(shard_id)

        if self.owner is not None:
            owner = self._state._client.guilds._add(self._owner)
            if owner is not None:
                self.owner_id = owner.id

        for role in self._roles:
            self.roles._add(role)

        for channel in self._channels:
            self._state._client.channels._add(channel)

        for member in self._members:
            self.members._add(member)

        del self._roles
        del self._channels
        del self._members
        del self._owner

    @property
    def owner(self):
        return self.members.get(self.owner_id)

    @property
    def afk_channel(self):
        return self._state._client.channels.get(self.afk_channel_id)

    @property
    def system_channel(self):
        return self._state._client.channels.get(self.system_channel_id)

    @property
    def widdget_channel(self):
        return self._state._client.channels.get(self.widget_channel_id)

    @property
    def rules_channel(self):
        return self._state._client.channels.get(self.rules_channel_id)
    
    @property
    def everyone_role(self):
        return self.roles.get(self.id)

    def to_preview_dict(self):
        return super().to_dict(cls=GuildPreview)

    def to_dict(self, cls=None):
        dct = super().to_dict(cls=cls)

        roles = []
        for role in self.roles:
            roles.append(role.to_dict())

        members = []
        for member in self.members:
            members.append(member.to_dict())

        channels = []
        for channel in self.channels:
            channels.append(channel.to_dict())

        dct['roles'] = roles
        dct['members'] = members
        dct['channels'] = channels

        return dct


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

    async def add(self, user, *, reason=None, delete_message_days=None):
        rest = self._client.rest
        resp = await rest.create_guild_ban(self._guild.id, user.id, delete_message_days, reason)
        data = await resp.json()
        ban = self._add(data)
        return ban

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
        rest = self._client.rest
        resp = await rest.get_guild(guild_id)
        data = await resp.json()
        guild = self._add(data)
        return guild

    async def fetch_preview(self, guild_id) -> GuildPreview:
        rest = self._client.rest
        resp = await rest.get_guild_preview(guild_id)
        data = await resp.json()
        perview = self._add(data).__preview
        return perview