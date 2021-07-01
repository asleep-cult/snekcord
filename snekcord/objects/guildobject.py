from datetime import datetime

from .baseobject import BaseObject
from .. import rest
from ..clients.client import ClientClasses
from ..enums import (
    ExplicitContentFilterLevel,
    GuildFeature,
    GuildNSFWLevel,
    MFALevel,
    MessageNotificationsLevel,
    PremiumTier,
    VerificationLevel)
from ..flags import SystemChannelFlags
from ..utils import _validate_keys
from ..utils.json import JsonArray, JsonField, JsonObject
from ..utils.snowflake import Snowflake

__all__ = ('Guild', 'GuildBan', 'WelcomeScreen', 'WelcomeScreenChannel')


class Guild(BaseObject):
    """Represents a Guild from Discord

    Attributes:
        widget GuildWidget: The guild's widget interface

        vanity_url GuildVanityURL: The guild's vanity url interface

        welcome_screen GuildWelcomeScreen: The guild's welcome screen interface

        channels GuildChannelState: The guild's channel state

        emojis GuildEmojiState: The guild's emoji state

        roles RoleState: The guild's role state

        members GuildMemberState: The guild's member state
    """
    __slots__ = ('unsynced', 'widget', 'vanity_url', 'welcome_screen', 'channels', 'emojis',
                 'roles', 'members', 'bans', 'integrations')

    name = JsonField('name')
    icon = JsonField('icon')
    splash = JsonField('splash')
    discovery_splash = JsonField('discovery_splash')
    features = JsonArray('features', GuildFeature.get_enum)
    member_count = JsonField('approximate_member_count')
    presence_count = JsonField('approximate_presence_count')
    description = JsonField('description')
    icon_hash = JsonField('icon_hash')
    owner = JsonField('owner')
    owner_id = JsonField('owner_id', Snowflake)
    permissions = JsonField('permissions')
    region = JsonField('region')
    afk_channel_id = JsonField('afk_channel_id', Snowflake)
    afk_timeout = JsonField('afk_timeout')
    verification_level = JsonField('verification_level', VerificationLevel.get_enum)
    default_message_notifications = JsonField(
        'default_message_notifications',
        MessageNotificationsLevel.get_enum
    )
    explicit_content_filter = JsonField(
        'explicit_content_filter',
        ExplicitContentFilterLevel.get_enum
    )
    mfa_level = JsonField('mfa_level', MFALevel.get_enum)
    application_id = JsonField('application_id', Snowflake)
    system_channel_id = JsonField('system_channel_id', Snowflake)
    system_channel_flags = JsonField('system_channel_flags', SystemChannelFlags.from_value)
    rules_channel_id = JsonField('rules_channel_id', Snowflake)
    joined_at = JsonField('joined_at', datetime.fromisoformat)
    large = JsonField('large')
    unavailable = JsonField('unavailable')
    member_count = JsonField('member_count')
    _voice_states = JsonArray('voice_states')
    _threads = JsonArray('threads')
    _presences = JsonArray('presences')
    max_presences = JsonField('max_presences')
    max_members = JsonField('max_members')
    banner = JsonField('banner')
    premium_tier = JsonField('permium_tier', PremiumTier.get_enum)
    premium_subscription_count = JsonField('premium_subscription_count')
    preferred_locale = JsonField('preferred_locale')
    public_updates_channel_id = JsonField('public_updates_channel_id', Snowflake)
    max_video_channel_users = JsonField('max_video_channel_users')
    nsfw_level = JsonField('nsfw', GuildNSFWLevel.get_enum)

    def __init__(self, *, state):
        super().__init__(state=state)

        self.unsynced = True

        self.widget = ClientClasses.GuildWidget.unmarshal(guild=self)
        self.vanity_url = ClientClasses.GuildVanityURL.unmarshal(guild=self)
        self.welcome_screen = ClientClasses.WelcomeScreen.unmarshal(guild=self)

        self.bans = ClientClasses.GuildBanState(client=self.state.client, guild=self)
        self.channels = ClientClasses.GuildChannelState(
            superstate=self.state.client.channels, guild=self)
        self.emojis = ClientClasses.GuildEmojiState(client=self.state.client, guild=self)
        self.roles = ClientClasses.RoleState(client=self.state.client, guild=self)
        self.members = ClientClasses.GuildMemberState(client=self.state.client, guild=self)
        self.integrations = ClientClasses.IntegrationState(client=self.state.client, guild=self)

    def __str__(self):
        return self.name

    async def sync(self, payload):
        cache_flags = self.state.client.cache_flags

        if cache_flags is None:
            return

        if self.unsynced and cache_flags.guild_bans:
            await self.bans.fetch_all()

        if self.unsynced and cache_flags.guild_integrations:
            await self.integrations.fetch_all()

        if self.unsynced and cache_flags.guild_invites:
            await self.fetch_invites()

        if 'widget_enabled' not in payload and cache_flags.guild_widget:
            await self.widget.fetch()

        self.unsynced = False

    async def modify(self, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), rest.modify_guild.json)

        data = await rest.modify_guild.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.id),
            json=kwargs)

        return self.state.upsert(data)

    async def delete(self):
        await rest.delete_guild.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.id))

    async def prune(self, **kwargs):
        remove = kwargs.pop('remove', True)

        try:
            roles = Snowflake.try_snowflake_set(kwargs['roles'])

            if remove:
                kwargs['include_roles'] = tuple(roles)
            else:
                kwargs['include_roles'] = ','.join(map(str, roles))
        except KeyError:
            pass

        if remove:
            keys = rest.begin_guild_prune.json
        else:
            keys = rest.get_guild_prune_count.params

        _validate_keys(f'{self.__class__.__name__}.prune',
                       kwargs, (), keys)

        if remove:
            data = await rest.begin_guild_prune.request(
                session=self.state.client.rest,
                fmt=dict(guild_id=self.id),
                json=kwargs)
        else:
            data = await rest.get_guild_prune_count.request(
                session=self.state.client.rest,
                fmt=dict(guild_id=self.id),
                params=kwargs)

        return data['pruned']

    async def fetch_preview(self):
        return await self.state.fetch_preview(self.id)

    async def fetch_voice_regions(self):
        data = await rest.get_guild_voice_regions.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.id))

        return data

    async def fetch_invites(self):
        data = await rest.get_guild_invites.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.id))

        invites = []

        for invite in data:
            invites.append(self.state.client.invites.upsert(invite))

        return invites

    async def fetch_templates(self):
        data = await rest.get_guild_templates.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.id))

        return self.state.new_template_many(data)

    async def create_template(self, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.create_template',
                       kwargs, ('name',), rest.create_guild_template.json)

        data = await rest.create_guild_template.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.id),
            json=kwargs)

        return self.state.new_template(data)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        widget_data = {}

        if 'widget_channel_id' in data:
            widget_data['channel_id'] = data['widget_channel_id']

        if 'widget_enabled' in data:
            widget_data['enabled'] = data['widget_enabled']

        if widget_data:
            self.widget.update(widget_data)

        if 'vanity_url_code' in data:
            self.vanity_url.update({'code': data['vanity_url_code']})

        if 'channels' in data:
            for channel in data['channels']:
                channel['guild_id'] = self.id
                self.state.client.channels.upsert(channel)

        if 'emojis' in data:
            emojis = set()

            for emoji in data['emojis']:
                emojis.add(self.emojis.upsert(emoji).id)

            for emoji_id in set(self.emojis.keys()) - emojis:
                del self.emojis.mapping[emoji_id]

        if 'roles' in data:
            roles = set()

            for role in data['roles']:
                roles.add(self.roles.upsert(role).id)

            for role_id in set(self.roles.keys()) - roles:
                del self.emojis.mapping[role_id]

        if 'members' in data:
            for member in data['members']:
                self.members.upsert(member)

        if 'stage_instances' in data:
            for stage in data['stage_instances']:
                stage['guild_id'] = self.id
                self.state.client.stages.upsert(stage)

        if 'welcome_screen' in data:
            self.welcome_screen.update(data['welcome_screen'])


class GuildBan(BaseObject):
    __slots__ = ('user',)

    reason = JsonField('reason')

    @property
    def guild(self):
        return self.state.guild

    async def revoke(self):
        await self.state.remove(self.user)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.client.users.upsert(user)
            self._json_data_['id'] = self.user.id


class WelcomeScreenChannel(JsonObject):
    """Represents a channel in a `WelcomeScreen`

    Attributes:
        channel_id Snowflake: The id of the channel that this welcome channel
            refers to

        description str: The welcome channel's description

        emoji_id Snowflake: The id of the welcome channel's emoji

        emoji_name str: The name of the welcome channel's emoji

        welcome_screen WelcomeScreen: The welcome screen associated with the
            welcome channel
    """
    __slots__ = ('welcome_screen',)

    channel_id = JsonField('channel_id', Snowflake)
    description = JsonField('description')
    emoji_id = JsonField('emoji', Snowflake)
    emoji_name = JsonField('emoji_name')

    def __init__(self, *, welcome_screen):
        self.welcome_screen = welcome_screen

    @property
    def channel(self):
        """The channel that this welcome channel refers to

        warning:
            This property relies on the channel cache so it could return None
        """
        return self.welcome_screen.guild.channels.get(self.channel_id)

    @property
    def emoji(self):
        """The welcome channel's emoji

        warning:
            This property relies on the emoji cache so it could return None
        """
        return self.welcome_screen.guild.emojis.get(self.emoji_id)


class WelcomeScreen(JsonObject):
    """Represents a `Guild`'s welcome screen

    Attributes:
        description str: The welcome screen's description

        guild Guild: The guild associated with the welcome screen

        welcome_channels list[WelcomeChannel]: The welcome screen's channels
    """
    __slots__ = ('guild', 'welcome_channels')

    channel_id = JsonField('channel_id', Snowflake)

    def __init__(self, *, guild):
        self.guild = guild
        self.welcome_channels = []

    async def fetch(self):
        """Invokes an API request to get the welcome screen

        Returns:
            WelcomeScreen: The updated welcome screen
        """
        data = await rest.get_guild_welcome_screen.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        self.update(data)

        return self

    async def modify(self, **kwargs):
        """Invokes an API request to modify the welcome screen

        **Parameters:**

        | Name             | Type | Description                                   |
        | ---------------- | ---- | --------------------------------------------- |
        | enabled          | bool | Whether or not the welcome screen is enabled  |
        | welcome_channels | dict | The new welcome channels `{channel: options}` |
        | description      | str  | The welcome screen's new description          |

        **Welcome Channel Options:**

        | Name        | Description                       |
        | ----------- | --------------------------------- |
        | description | The welcome channel's description |
        | emoji       | The welcome channel's emoji       |

        Returns:
            WelcomeScreen: The modified welcome screen

        Examples:
            ```py
            await guild.welcome_screen.modify(
                description='Welcome to this fantastic guild',
                enabled=True,
                welcome_channels={
                    8235356323523452: {
                        'description': 'Get roles here',
                        'emoji': some_emoji
                    },
                    7583857293758372: {
                        'description': 'Use bot commands here',
                        emoji: another_emoji
                    }
                }
            )
            ```
        """  # noqa: E501
        try:
            welcome_channels = []

            for key, value in kwargs['welcome_channels'].items():
                value['channel_id'] = Snowflake.try_snowflake(key)

                try:
                    emoji = value.pop('emoji')
                    value['emoji_id'] = emoji.id
                    value['emoji_name'] = emoji.name
                except KeyError:
                    pass

                _validate_keys(f'welcome_channels[{key}]', value, (),
                               ('channel_id', 'description', 'emoji_id', 'emoji_name'))

                welcome_channels.append(value)

            kwargs['welcome_channels'] = welcome_channels
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), rest.modify_guild_welcome_screen.json)

        data = await rest.modify_guild_welcome_screen.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id),
            json=kwargs)

        self.update(data)

        return self

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        welcome_channels = data.get('welcome_channels')
        if welcome_channels is not None:
            self.welcome_channels.clear()

            for channel in welcome_channels:
                channel = WelcomeScreenChannel.unmarshal(channel, welcome_screen=self)
                self.welcome_channels.append(channel)
