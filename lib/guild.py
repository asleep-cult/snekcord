from .invite import GuildInviteState

from .channel import (
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


class RoleTags(JsonStructure):
    __slots__ = ('bot_id', 'integration_id', 'premium_subscriber')

    __json_fields__ = {
        'bot_id': JsonField('bot_id', Snowflake, str),
        'integration_id': JsonField('integration_id', Snowflake, str),
        'premium_subscriber': JsonField('premium_subscriber'),
    }

    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: bool


class Role(BaseObject):
    __slots__ = (
        'id', 'name', 'color', 'hoist', 'position', 'permissions', 'managed',
        'mentionable', 'tags'
    )

    __json_fields__ = {
        'name': JsonField('name'),
        'color': JsonField('color'),
        'hoist': JsonField('hoist'),
        'position': JsonField('position'),
        'permissions': JsonField('permissions'),
        'managed': JsonField('managed'),
        'mentionable': JsonField('mentionable'),
        'tags': JsonField('tags', struct=RoleTags),
    }

    id: Snowflake
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: RoleTags
    guild: ...

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
        resp = await rest.modify_guild_role_permissions(
            self._guild.id,
            positions
        )
        data = await resp.json()
        roles = []
        for role in data:
            role = self._add(role)
            roles.append(role)
        return roles


class GuildMember(JsonStructure):
    __json_slots__ = (
        '_user', 'nick', '_roles', 'joined_at', 'premium_since',
        'deaf', 'mute', 'pending', '_state', 'guild', 'user'
    )

    __json_fields__ = {
        '_user': JsonField('user'),
        'nick': JsonField('nick'),
        '_roles': JsonField('roles'),
        'joined_at': JsonField('joined_at'),
        'premium_since': JsonField('premium_since'),
        'deaf': JsonField('deaf'),
        'mute': JsonField('mute'),
        'pending': JsonField('pending'),
    }

    _user: ...
    nick: str
    _roles: list
    joined_at: str
    premium_since: str
    deaf: bool
    mute: bool
    pending: bool

    def __init__(
        self,
        *,
        state: 'GuildMemberState',
        guild: 'Guild',
        user=None
    ):
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

    def _update(self, *args, **kwargs):
        pass

    async def edit(
        self,
        nick=None,
        roles=None,
        mute=None,
        deaf=None,
        channel=None
    ):
        rest = self._state._client.rest

        if channel is not None:
            channel = channel.id

        resp = await rest.modify_guild_member(
            self.guild.id, self.user.id, roles=roles,
            mute=mute, deaf=deaf, channel=channel
        )
        data = await resp.json()
        member = self._state._add(data)
        return member

    async def ban(self, *, reason=None, delete_message_days=None):
        ban = await self.guild.bans.add(
            self,
            reason=reason,
            delete_message_days=delete_message_days
        )
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
        await rest.add_guild_member_role(
            self._member.guild.id,
            self._member.id,
            role.id
        )

    async def remove(self, role):
        rest = self._client.rest
        await rest.remove_guild_member_role(
            self._member.guild.id,
            self._member.id,
            role.id
        )


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
        member = GuildMember.unmarshal(
            data,
            state=self,
            guild=self._guild,
            user=user
        )
        self._values[member.user.id] = member
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

    async def add(
        self,
        user,
        access_token,
        *,
        nick=None,
        roles=None,
        mute=None,
        deaf=None
    ):
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
    __json_fields__ = {
        'name': JsonField('name'),
        '_roles': JsonArray('roles'),
        '_user': JsonField('user'),
        'required_colons': JsonField('required_colons'),
        'managed': JsonField('managed'),
        'animated': JsonField('animated'),
        'available': JsonField('available'),
    }

    id: Snowflake
    name: ...
    _roles: ...
    _user: ...
    required_colons: ...
    managed: ...
    animated: ...
    available: ...

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
        return '<GuildEmoji String: %r, Roles: %s, Guild: %s>' % (
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
        resp = await rest.create_guild_emoji(
            self._guild.id,
            name,
            image,
            roles
        )
        data = await resp.json()
        emoji = self._add(data)
        return emoji


class GuildIntegrationAccount(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
    }

    id: Snowflake
    name: ...


class GuildIntegrationApplication(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'icon': JsonField('icon'),
        'description': JsonField('description'),
        'summary': JsonField('summary'),
        '_bot': JsonField('bot'),
    }

    id: Snowflake
    name: ...
    icon: ...
    description: ...
    summary: ...
    _bot: ...

    def __init__(self, state):
        self._state = state

        if self._bot is not None:
            self.bot = self._state._client.users.add(self._bot)


class GuildIntegration(BaseObject):
    __json_fields__ = {
        'name':  JsonField('name'),
        'type': JsonField('type'),
        'enabled': JsonField('enabled'),
        'syncing': JsonField('syncing'),
        'role_id': JsonField('role_id', Snowflake, str),
        'enable_emoticons': JsonField('enable_emoticons'),
        'expire_behavior': JsonField('expire_behavior'),
        'expire_grace_period': JsonField('expire_grace_period'),
        '_user': JsonField('user'),
        'account': JsonField('account', struct=GuildIntegrationAccount),
        'synced_at': JsonField('synced_at'),
        'subscriber_count': JsonField('subscriber_count'),
        'revoked': JsonField('revoked'),
        '_application': JsonField('application'),
    }

    id: Snowflake
    name: ...
    type: ...
    enabled: ...
    syncing: ...
    role_id: ...
    enable_emoticons: ...
    expire_behavior: ...
    expire_grace_period: ...
    _user: ...
    account: ...
    synced_at: ...
    subscriber_count: ...
    revoked: ...
    _application: ...

    def __init__(self, state, guild):
        self._state = state
        self.guild = guild

        if self._user is not None:
            self.user = self._state._client.users._add(self._user)

        if self._application is not None:
            self.application = GuildIntegrationApplication.unmarshal(
                self._application,
                state=self._state
            )

    async def edit(
        self,
        *,
        expire_behavior=None,
        expire_grace_period=None,
        enable_emoticons=None
    ):
        rest = self._state._client.rest
        await rest.modify_guild_integration(
            self.guild.id, self.id, expire_behavior=expire_behavior,
            expire_grace_period=expire_grace_period,
            enable_emoticons=enable_emoticons
        )

    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_guild_integration(self.guild.id, self.id)

    async def sync(self):
        rest = self._state._client.rest
        await rest.delete_guild_integration(self.guild.id, self.id)


class GuildIntegrationState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data):
        integration = self.get(data['id'])
        if integration is not None:
            integration._update(data)
            return integration
        integration = GuildIntegration.unmarshal(
            data,
            state=self,
            guild=self._guild
        )
        self._values[integration.id] = integration
        return integration

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_guild_integrations(self._guild.id)
        data = await resp.json()
        integrations = []
        for integration in data:
            integration = self._add(integration)
            integrations.append(integration)
        return integrations

    async def create(self, integration_id, integration_type):
        rest = self._client.rest
        await rest.create_guild_integration(integration_type, integration_id)


class GuildWidgetChannel(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'poosition': JsonField('position'),
    }

    name: ...
    poosition: ...


class GuildWidgetMember(BaseObject):
    __json_fields__ = {
        'username': JsonField('username'),
        'discriminator': JsonField('discriminator'),
        'avatar': JsonField('avatar'),
        'avatar_url': JsonField('avatar_url'),
    }

    username: ...
    discriminator: ...
    avatar: ...
    avatar_url: ...


class GuildWidget(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'instant_invite': JsonField('instant_invite'),
        'channels': JsonArray('channels', struct=GuildWidgetChannel),
        'members': JsonArray('members', struct=GuildWidgetMember),
        'presence_count': JsonField('presence_count'),
    }

    id: Snowflake
    name: ...
    instant_invite: ...
    channels: ...
    members: ...
    presence_count: ...

    def __init__(self, guild):
        self.guild = guild

    def edit(self, *, enabled=None, channel=None):
        return self.guild.edit_widget(enabled=enabled, channel=channel)


class GuildWidgetSettings(JsonStructure):
    __json_fields__ = {
        'enabled': JsonField('enabled'),
        'channel_id': JsonField('channel_id'),
    }

    enabled: ...
    channel_id: ...
    channel: ...

    def __init__(self, guild):
        channels = guild._state._client.channels
        self.channel = channels.get(self.channel_id)


class PartialInvite(JsonStructure):
    __json_fields__ = {
        'code': JsonField('code'),
        'uses': JsonField('uses'),
    }

    code: ...
    uses: ...


class GuildPreview(BaseObject):
    # Basically a partial guild?
    __json_fields__ = {
        'name': JsonField('name'),
        'icon': JsonField('icon'),
        'splash': JsonField('splash'),
        'discovery_splash': JsonField('discovery_splash'),
        '_emojis': JsonArray('emojis'),
        'features': JsonArray('features'),
        'member_count': JsonField('approximate_member_count'),
        'presence_count': JsonField('approximate_presence_count'),
        'description': JsonField('description'),
    }

    id: Snowflake
    name: ...
    icon: ...
    splash: ...
    discovery_splash: ...
    _emojis: ...
    features: ...
    member_count: ...
    presence_count: ...
    description: ...

    def __init__(self, state):
        self._state = state
        self.emojis = GuildEmojiState(
            self._state._client,
            guild=self
        )
        self.roles: Iterable[Role] = RoleState(
            self._state._client,
            guild=self
        )
        self.members: Iterable[GuildMember] = GuildMemberState(
            self._state._client,
            guild=self
        )
        self.invites = GuildInviteState(
            self._state._client.invites,
            guild=self
        )
        self.bans = GuildBanState(
            self._state._client,
            guild=self
        )
        self.channels = GuildChannelState(
            self._state._client.channels,
            guild=self
        )
        self.integrations = GuildIntegrationState(
            self._state._client,
            guild=self
        )

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
        invite = PartialInvite.unmarshal(data)
        return invite

    async def get_prune_count(self, *, days=None, include_roles=None):
        rest = self._state.client.rest
        resp = await rest.get_guild_prune_count(self.id, days, include_roles)
        data = await resp.json()
        return data['pruned']

    async def begin_prune(
        self,
        days=None,
        include_roles=None,
        compute_prune_count=None
    ):
        rest = self._state._client.rest
        resp = await rest.begin_guild_prune(
            self.id,
            days=days,
            include_roles=include_roles,
            compute_prune_count=compute_prune_count
        )
        data = await resp.json()
        return data['pruned']

    async def fetch_widget(self):
        rest = self._state._client.rest
        resp = await rest.get_guild_widget(self.id)
        data = await resp.json()
        widget = GuildWidget.unmarshal(data)
        return widget

    async def fetch_widget_settings(self):
        rest = self._state._client.rest
        resp = await rest.get_guild_widget_settings(self.id)
        data = await resp.json()
        settings = GuildWidgetSettings.unmarshal(data, guild=self)
        return settings

    async def edit_widget_settings(self, *, enabled=None, channel=None):
        rest = self._state._client.rest

        if channel is not None:
            channel = channel.id

        resp = await rest.modify_guild_widget(
            self.id,
            enabled=enabled,
            channel_id=channel
        )
        data = await resp.json()
        widget = GuildWidgetSettings.unmarshal(data, guild=self)
        return widget

    def to_dict(self, cls=None):
        dct = super().to_dict(cls=cls)

        emojis = []
        for emoji in self.emojis:
            emojis.append(emoji.to_dict())

        dct['emojis'] = emojis

        return dct


class GuildBan(JsonStructure):
    __json_fields__ = {
        'reason': JsonField('reason'),
        '_user': JsonField('user'),
    }

    reason: ...
    _user: ...
    user: ...

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
        resp = await rest.create_guild_ban(
            self._guild.id,
            user.id,
            delete_message_days,
            reason
        )
        data = await resp.json()
        ban = self._add(data)
        return ban

    async def remove(self, user):
        rest = self._client.rest
        await rest.remove_guild_ban(self._guild.id, user.id)


class Guild(GuildPreview):
    __json_fields__ = {
        **GuildPreview.__json_fields__,
        'icon_hash': JsonField('icon_hash'),
        '_owner': JsonField('owner'),
        'owner_id': JsonField('owner_id', Snowflake, str),
        'permissions': JsonField('permissions'),
        'region': JsonField('region'),
        'afk_channel_id': JsonField('afk_channel_id', Snowflake, str),
        'afk_timeout': JsonField('afk_timeout'),
        'widget_enabled': JsonField('widget_enabled'),
        'widget_channel_id': JsonField('widget_channel_id', Snowflake, str),
        'verification_level': JsonField('verification_level'),
        'default_message_notifications': JsonField(
            'default_message_notifications'
        ),
        'explicit_content_filter': JsonField('explicit_content_filter'),
        '_roles': JsonArray('roles'),
        'mfa_level': JsonField('mfa_level'),
        'application_id': JsonField('application_id', Snowflake, str),
        'system_channel_id': JsonField('system_channel_id', Snowflake, str),
        'system_channel_flags': JsonField('system_channel_flags'),
        'rules_channel_id': JsonField('rules_channel_id', Snowflake, str),
        'joined_at': JsonField('joined_at'),
        'large': JsonField('large'),
        'unavailable': JsonField('unavailable'),
        'member_count': JsonField('member_count'),
        '_voice_states': JsonArray('voice_states'),
        '_members': JsonArray('members'),
        '_channels': JsonArray('channels'),
        '_presences': JsonArray('presences'),
        'max_presences': JsonField('max_presences'),
        'max_members': JsonField('max_members'),
        'vanity_url_code': JsonField('vanity_url_code'),
        'banner': JsonField('banner'),
        'premium_tier': JsonField('permium_tier'),
        'premium_subscription_count': JsonField('premium_subscription_count'),
        'preferred_locale': JsonField('preferred_locale'),
        'public_updates_channel_id': JsonField(
            'public_updates_channel_id',
            Snowflake,
            str
        ),
        'max_video_channel_users': JsonField('max_video_channel_users'),
    }

    id: Snowflake
    name: ...
    icon: ...
    splash: ...
    discovery_splash: ...
    _emojis: ...
    features: ...
    member_count: ...
    presence_count: ...
    description: ...
    icon_hash: ...
    _owner: ...
    owner_id: ...
    permissions: ...
    region: ...
    afk_channel_id: ...
    afk_timeout: ...
    widget_enabled: ...
    widget_channel_id: ...
    verification_level: ...
    default_message_notifications: ...
    explicit_content_filter: ...
    _roles: ...
    mfa_level: ...
    application_id: ...
    system_channel_id: ...
    system_channel_flags: ...
    rules_channel_id: ...
    joined_at: ...
    large: ...
    unavailable: ...
    member_count: ...
    _voice_states: ...
    _members: ...
    _channels: ...
    _presences: ...
    max_presences: ...
    max_members: ...
    vanity_url_code: ...
    banner: ...
    premium_tier: ...
    premium_subscription_count: ...
    preferred_locale: ...
    public_updates_channel_id: ...
    max_video_channel_users: ...

    def __init__(self, *, state: 'GuildState'):
        super().__init__(state)

        if self.owner is not None:
            owner = self._state._client.guilds._add(self._owner)
            if owner is not None:
                self.owner_id = owner.id

        for role in self._roles:
            self.roles._add(role)

        for channel in self._channels:
            self._state._client.channels._add(channel, guild=self)

        for member in self._members:
            self.members._add(member)

        del self._roles
        del self._channels
        del self._members
        del self._owner

    @property
    def shard(self):
        shard_id = ((self.id >> 22) % len(self._state._client.ws.shards))
        return self._state._client.ws.shards.get(shard_id)

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

    async def fetch_preview(self, guild_id):
        rest = self._client.rest
        resp = await rest.get_guild_preview(guild_id)
        data = await resp.json()
        guild = self._add(data)
        return guild
