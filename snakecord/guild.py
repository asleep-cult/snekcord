from .invite import GuildInviteState
from .user import User
from .channel import GuildChannelState
from .bases import BaseObject, BaseState
from .utils import JsonStructure, JsonField, JsonArray, Snowflake, JSON
from .member import GuildMemberState
from .emoji import GuildEmojiState
from .role import RoleState
from .integration import GuildIntegrationState
from .invite import PartialInvite
from typing import List, Optional


class GuildWidgetChannel(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'poosition': JsonField('position'),
    }

    name: str
    poosition: int


class GuildWidgetMember(BaseObject):
    __json_fields__ = {
        'username': JsonField('username'),
        'discriminator': JsonField('discriminator'),
        'avatar': JsonField('avatar'),
        'avatar_url': JsonField('avatar_url'),
    }

    username: str
    discriminator: str
    avatar: Optional[str]
    avatar_url: Optional[str]


class GuildWidget(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'instant_invite': JsonField('instant_invite'),
        'channels': JsonArray('channels', struct=GuildWidgetChannel),
        'members': JsonArray('members', struct=GuildWidgetMember),
        'presence_count': JsonField('presence_count'),
    }

    id: Snowflake
    name: str
    instant_invite: str
    channels: List[GuildWidgetChannel]
    members: List[GuildWidgetMember]
    presence_count: int

    def __init__(self, guild):
        self.guild = guild

    def edit(self, *, enabled=None, channel=None):
        return self.guild.edit_widget(enabled=enabled, channel=channel)


class GuildWidgetSettings(JsonStructure):
    __json_fields__ = {
        'enabled': JsonField('enabled'),
        'channel_id': JsonField('channel_id'),
    }

    enabled: bool
    channel_id: Snowflake

    def __init__(self, guild):
        self.guild = guild

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        channels = self.guild._state._client.channels
        self.channel = channels.get(self.channel_id)


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
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    _emojis: List[JSON]
    features: List[str]
    member_count: int
    presence_count: int
    description: Optional[str]

    def __init__(self, state):
        self._state = state
        self.members = GuildMemberState(
            self._state._client,
            guild=self
        )
        self.emojis = GuildEmojiState(
            self._state._client,
            guild=self
        )
        self.roles = RoleState(
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

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        emojis_seen = set()

        for emoji in self._emojis:
            emoji = self.emojis._add(emoji)
            emojis_seen.add(emoji.id)

        for emoji in self.emojis:
            if emoji.id not in emojis_seen:
                self.emojis.pop(emoji.id)


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
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    _emojis: List[JSON]
    features: List[str]
    member_count: int
    presence_count: int
    description: Optional[str]
    icon_hash: Optional[str]
    _owner: Optional[JSON]
    owner_id: Snowflake
    _permissions: Optional[str]
    region: str
    afk_channel_id: Optional[Snowflake]
    afk_timeout: int
    widget_enabled: Optional[bool]
    widget_channel_id: Optional[Snowflake]
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    _roles: List[JSON]
    mfa_level: int
    application_id: Optional[int]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: int
    rules_channel_id: Optional[Snowflake]
    joined_at: Optional[str]
    large: Optional[bool]
    unavailable: Optional[bool]
    member_count: Optional[int]
    _voice_states: Optional[List[JSON]]
    _members: Optional[List[JSON]]
    _channels: Optional[List[JSON]]
    _presences: Optional[List[JSON]]
    max_presences: Optional[int]
    max_members: Optional[int]
    vanity_url_code: Optional[str]
    banner: Optional[str]
    premium_tier: int
    premium_subscription_count: Optional[int]
    preferred_locale: str
    public_updates_channel_id: Optional[Snowflake]
    max_video_channel_users: Optional[int]

    def __init__(self, *, state: 'GuildState'):
        super().__init__(state)

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
    def widget_channel(self):
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

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        channels_seen = set()
        members_seen = set()
        roles_seen = set()

        for channel in self._channels:
            channel = self._state._client.channels._add(channel, guild=self)
            channels_seen.add(channel.id)

        for member in self._members:
            member = self.members._add(member)
            members_seen.add(member.user.id)

        for role in self._roles:
            role = self.roles._add(role)
            roles_seen.add(role.id)

        for channel in self.channels:
            if channel.id not in channels_seen:
                self.channels.pop(channel.id)

        for member in self.members:
            if member.user.id not in members_seen:
                self.members.pop(member.id)

        for role in self.roles:
            if role.id not in roles_seen:
                self.roles.pop(role.id)

        if self._owner is not None:
            owner = self._state._client.guilds._add(self._owner)
            if owner is not None:
                self.owner_id = owner.id


class GuildState(BaseState):
    __state_class__ = Guild

    def _add(self, data) -> Guild:
        guild = self.get(data['id'])
        if guild is not None:
            guild._update(data, set_default=False)
            return guild
        guild = self.__state_class__.unmarshal(data, state=self)
        self._values[guild.id] = guild
        self._client.events.guild_cache(guild)
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


class GuildBan(JsonStructure):
    __json_fields__ = {
        'reason': JsonField('reason'),
        '_user': JsonField('user'),
    }

    reason: str
    _user: JSON

    def __init__(self, state, user):
        self._state = state
        self.user: User = user

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        self.user = self._state._client._users.add(self._user)

        del self._user


class GuildBanState(BaseState):
    __state_class__ = GuildBan

    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data):
        ban = self.get(data['user']['id'])
        if ban is not None:
            ban._update(data, set_default=False)
            return ban
        ban = self.__state_class__.unmarshal(
            data,
            state=self
        )
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
