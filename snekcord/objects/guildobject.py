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
    VerificationLevel
)
from ..flags import SystemChannelFlags
from ..resolvers import resolve_image_data
from ..utils import JsonArray, JsonField, JsonObject, Snowflake, undefined

__all__ = ('Guild', 'GuildBan', 'WelcomeScreen', 'WelcomeScreenChannel')


class Guild(BaseObject):
    __slots__ = (
        'unsynced', 'widget', 'vanity_url', 'welcome_screen', 'channels', 'emojis', 'roles',
        'members', 'bans', 'integrations'
    )

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
            superstate=self.state.client.channels, guild=self
        )
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

    def fetch_preview(self):
        return self.state.fetch_preview(self.id)

    def fetch_voice_regions(self):
        return rest.get_guild_voice_regions.request(
            self.state.client.rest, {'guild_id': self.id}
        )

    async def fetch_invites(self):
        data = await rest.get_guild_invites.request(
            self.state.client.rest, {'guild_id': self.id}
        )

        return [self.state.client.invites.upsert(invite) for invite in data]

    async def fetch_templates(self):
        data = await rest.get_guild_templates.request(
            self.state.client.rest, {'guild_id': self.id}
        )

        return [self.state.new_template(template) for template in data]

    async def create_template(self, *, name, description=undefined):
        json = {'name': str(name)}

        if description is not undefined:
            if description is not None:
                json['description'] = str(description)
            else:
                json['description'] = None

        data = await rest.create_guild_template.request(
            self.state.client.rest, {'guild_id': self.id},
            json=json
        )

        return self.state.new_template(data)

    async def modify(
        self, *, name=None, verification_level=undefined,
        default_message_notifications=undefined, explicit_content_filter=undefined,
        afk_channel=undefined, afk_timeout=None, icon=undefined, owner=None,
        splash=undefined, discovery_splash=undefined, banner=undefined, system_channel=undefined,
        system_channel_flags=None, rules_channel=undefined, public_updates_channel=undefined,
        preferred_locale=undefined, features=None, description=undefined
    ):
        json = {}

        if name is not None:
            json['name'] = str(name)

        if verification_level is not undefined:
            if verification_level is not None:
                json['verification_level'] = VerificationLevel.get_value(verification_level)
            else:
                json['verification_level'] = None

        if default_message_notifications is not undefined:
            if default_message_notifications is not None:
                json['default_message_notifications'] = (
                    MessageNotificationsLevel.get_value(default_message_notifications)
                )
            else:
                json['default_message_notifications'] = None

        if explicit_content_filter is not undefined:
            if explicit_content_filter is not None:
                json['explicit_content_filter'] = (
                    ExplicitContentFilterLevel.get_value(explicit_content_filter)
                )
            else:
                json['explicit_content_filter'] = None

        if afk_channel is not undefined:
            if afk_channel is not None:
                json['afk_channel_id'] = Snowflake.try_snowflake(afk_channel)
            else:
                json['afk_channel_id'] = None

        if afk_timeout is not None:
            json['afk_timeout'] = int(afk_timeout)

        if icon is not undefined:
            if icon is not None:
                json['icon'] = resolve_image_data(icon)
            else:
                json['icon'] = None

        if owner is not None:
            json['owner_id'] = Snowflake.try_snowflake(owner)

        if splash is not undefined:
            if splash is not None:
                json['splash'] = resolve_image_data(splash)
            else:
                json['splash'] = None

        if discovery_splash is not undefined:
            if discovery_splash is not None:
                json['discovery_splash'] = resolve_image_data(discovery_splash)
            else:
                json['discovery_splash'] = None

        if banner is not undefined:
            if banner is not None:
                json['banner'] = resolve_image_data(banner)
            else:
                json['banner'] = None

        if system_channel is not undefined:
            if system_channel is not None:
                json['system_channel_id'] = Snowflake.try_snowflake(system_channel)
            else:
                json['system_channel_id'] = None

        if system_channel_flags is not None:
            json['system_channel_flags'] = SystemChannelFlags.get_value(system_channel_flags)

        if rules_channel is not undefined:
            if rules_channel is not None:
                json['rules_channel_id'] = Snowflake.try_snowflake(rules_channel)
            else:
                json['rules_channel_id'] = None

        if public_updates_channel is not undefined:
            if public_updates_channel is not None:
                json['public_updates_channel_id'] = Snowflake.try_snowflake(public_updates_channel)
            else:
                json['public_updates_channel_id'] = None

        if preferred_locale is not undefined:
            if preferred_locale is not undefined:
                json['preferred_locale'] = str(preferred_locale)
            else:
                json['preferred_locale'] = None

        if features is not None:
            json['features'] = [GuildFeature.get_value(feature) for feature in features]

        if description is not undefined:
            if description is not None:
                json['description'] = str(description)
            else:
                json['description'] = None

        data = await rest.modify_guild.request(
            self.client.rest, {'guild_id': self.id}, json=json
        )

        return self.state.upsert(data)

    async def fetch_prune_count(self, *, days=None, roles=None):
        params = {}

        if days is not None:
            params['days'] = int(days)

        if roles is not None:
            params['include_roles'] = ','.join(str(r) for r in Snowflake.try_snowflake_set(roles))

        data = await rest.get_guild_prune_count.request(
            self.state.client.rest, {'guild_id': self.guild.id}, params=params
        )

        return data['pruned']

    async def begin_prune(self, *, days=None, compute_count=None, roles=None, reason=None):
        json = {}

        if days is not None:
            json['days'] = int(days)

        if compute_count is not None:
            json['compute_count'] = bool(compute_count)

        if roles is not None:
            json['roles'] = Snowflake.try_snowflake_set(roles)

        if reason is not None:
            json['reason'] = str(reason)

        data = await rest.begin_guild_prune.request(
            self.state.client.rest, {'guild_id': self.id}, json=json
        )

        return data['pruned']

    async def leave(self):
        return self.state.leave(self.id)

    async def delete(self):
        return self.state.delete(self.id)

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
