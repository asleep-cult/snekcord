from . import structures
from .channel import GuildChannelState
from .emoji import GuildEmojiState
from .integration import GuildIntegrationState
from .invite import GuildInviteState
from .member import GuildMemberState
from .role import RoleState
from .state import BaseState
from .utils import _try_snowflake, undefined


class GuildWidget(structures.GuildWidget):
    def __init__(self, guild=None):
        self.guild = guild

    def edit(self, *, enabled=None, channel=None):
        return self.guild.edit_widget(enabled=enabled, channel=channel)


class GuildWidgetSettings(structures.GuildWidgetSettings):
    def __init__(self, guild=None):
        self.guild = guild

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        channels = self.guild._state.client.channels
        self.channel = channels.get(self.channel_id)


class GuildPreview(structures.GuildPreview):
    def __init__(self, state):
        self._state = state
        self.members = GuildMemberState(self._state.client, guild=self)
        self.emojis = GuildEmojiState(self._state.client, guild=self)
        self.roles = RoleState(self._state.client, guild=self)
        self.invites = GuildInviteState(self._state.client.invites, guild=self)
        self.bans = GuildBanState(self._state.client, guild=self)
        self.channels = GuildChannelState(self._state.client.channels, guild=self)
        self.integrations = GuildIntegrationState(self._state.client, guild=self)

    async def edit(self, **kwargs):
        rest = self._state.client.rest

        afk_channel = kwargs.pop('afk_channel', undefined)
        if afk_channel is not undefined:
            afk_channel = _try_snowflake(afk_channel)

        owner = kwargs.pop('owner', undefined)
        if owner is not undefined:
            owner = _try_snowflake(owner)

        system_channel = kwargs.pop('system_channel', undefined)
        if system_channel is not undefined:
            system_channel = _try_snowflake(system_channel)

        rules_channel = kwargs.pop('rules_channel', undefined)
        if rules_channel is not undefined:
            rules_channel = _try_snowflake(rules_channel)

        public_updates_channel = kwargs.pop('public_updates_channel', undefined)
        if public_updates_channel is not undefined:
            public_updates_channel = _try_snowflake(public_updates_channel)

        await rest.modify_guild(
            **kwargs, afk_channel_id=afk_channel, owner_id=owner,
            system_channel_id=system_channel, rules_channel_id=rules_channel,
            public_updates_channel_id=public_updates_channel
        )

    async def delete(self):
        rest = self._state.client.rest
        await rest.delete_guild(self.id)

    async def fetch_voice_region(self):
        rest = self._state.client.rest
        data = await rest.get_guild_voice_region(self.id)
        return data

    async def fetch_vanity_url(self):
        rest = self._state.client.rest
        data = await rest.get_guild_vanity_url(self.id)
        invite = structures.PartialInvite.unmarshal(data)
        return invite

    async def get_prune_count(self, *, days=None, include_roles=None):
        rest = self._state.client.rest
        data = await rest.get_guild_prune_count(self.id, days, include_roles)
        return data['pruned']

    async def begin_prune(
        self,
        days=None,
        include_roles=None,
        compute_prune_count=None
    ):
        rest = self._state.client.rest
        resp = await rest.begin_guild_prune(
            self.id,
            days=days,
            include_roles=include_roles,
            compute_prune_count=compute_prune_count
        )
        data = await resp.json()
        return data['pruned']

    async def fetch_widget(self):
        rest = self._state.client.rest
        resp = await rest.get_guild_widget(self.id)
        data = await resp.json()
        widget = GuildWidget.unmarshal(data)
        return widget

    async def fetch_widget_settings(self):
        rest = self._state.client.rest
        resp = await rest.get_guild_widget_settings(self.id)
        data = await resp.json()
        settings = GuildWidgetSettings.unmarshal(data, guild=self)
        return settings

    async def edit_widget_settings(self, *, enabled=None, channel=None):
        rest = self._state.client.rest

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
        structures.GuildPreview._update(*args, **kwargs)
        emojis_seen = set()

        for emoji in self._emojis:
            emoji = self.emojis._add(emoji)
            emojis_seen.add(emoji.id)

        for emoji in self.emojis:
            if emoji.id not in emojis_seen:
                self.emojis.pop(emoji.id)


class Guild(GuildPreview, structures.Guild):
    def __init__(self, *, state: 'GuildState'):
        super().__init__(state)

    @property
    def shard(self):
        shard_id = ((self.id >> 22) % len(self._state.client.ws.shards))
        return self._state.client.ws.shards.get(shard_id)

    @property
    def owner(self):
        return self.members.get(self.owner_id)

    @property
    def afk_channel(self):
        return self.channels.get(self.afk_channel_id)

    @property
    def system_channel(self):
        return self.channels.get(self.system_channel_id)

    @property
    def widget_channel(self):
        return self.channels.get(self.widget_channel_id)

    @property
    def rules_channel(self):
        return self.channels.get(self.rules_channel_id)

    @property
    def everyone_role(self):
        return self.roles.get(self.id)

    def to_preview_dict(self):
        return super().to_dict(cls=GuildPreview)

    def to_dict(self, cls=None):
        dct = super().to_dict(cls=cls)

        dct['roles'] = [role.to_dict() for role in self.roles]
        dct['members'] = [member.to_dict() for member in self.members]
        dct['channels'] = [channel.to_dict() for channel in self.channels]

        return dct

    def _update(self, *args, **kwargs):
        GuildPreview._update(self, *args, **kwargs)
        channels_seen = set()
        members_seen = set()
        roles_seen = set()

        for channel in self._channels:
            channel = self._state.client.channels._add(channel, guild=self)
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
            owner = self._state.client.guilds._add(self._owner)
            if owner is not None:
                self.owner_id = owner.id


class GuildBan(structures.GuildBan):
    def __init__(self, state, user=None):
        self._state = state
        self.user = user

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        self.user = self._state.client.users._add(self.user)


class GuildState(BaseState):
    def _add(self, data) -> Guild:
        guild = self.get(data['id'])
        if guild is not None:
            guild._update(data)
            return guild

        guild = Guild.unmarshal(data, state=self)
        self._items[guild.id] = guild
        self.client.events.guild_cache(guild)
        return guild

    async def fetch(self, guild_id) -> Guild:
        rest = self.client.rest
        data = await rest.get_guild(guild_id)
        guild = self._add(data)
        return guild

    async def fetch_preview(self, guild_id):
        rest = self.client.rest
        data = await rest.get_guild_preview(guild_id)
        guild = self._add(data)
        return guild


class GuildBanState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self.guild = guild

    def _add(self, data):
        ban = self.get(data['user']['id'])
        if ban is not None:
            ban._update(data)
            return ban

        ban = GuildBan.unmarshal(data, state=self)
        self._items[ban.user.id] = ban
        return ban

    async def fetch(self, user):
        rest = self.client.rest
        data = await rest.get_guild_ban(self.guild.id, user.id)
        ban = self._add(data)
        return ban

    async def fetch_all(self):
        rest = self.client.rest
        data = await rest.get_guild_bans(self.guild.id)
        bans = [self._add(ban) for ban in data]
        return bans

    async def add(self, user, **kwargs):
        rest = self.client.rest
        user = _try_snowflake(user)
        data = await rest.create_guild_ban(self.guild.id, user.id)
        ban = self._add(data)
        return ban

    async def remove(self, user):
        rest = self.client.rest
        user = _try_snowflake(user)
        await rest.remove_guild_ban(self.guild.id, user)
