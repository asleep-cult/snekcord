from .baseobject import BaseObject, BaseTemplate
from .inviteobject import GuildVanityURL
from .widgetobject import GuildWidget
from .. import rest
from ..utils import (JsonArray, JsonField, JsonObject, JsonTemplate, Snowflake,
                     _validate_keys)

__all__ = ('Guild', 'GuildBan', 'WelcomeScreen', 'WelcomeScreenChannel')


GuildPreviewTemplate = JsonTemplate(
    name=JsonField('name'),
    icon=JsonField('icon'),
    splash=JsonField('splash'),
    discovery_splash=JsonField('discovery_splash'),
    features=JsonArray('features'),
    member_count=JsonField('approximate_member_count'),
    presence_count=JsonField('approximate_presence_count'),
    description=JsonField('description'),
    __extends__=(BaseTemplate,)
)


GuildTemplate = JsonTemplate(
    icon_hash=JsonField('icon_hash'),
    owner=JsonField('owner'),
    owner_id=JsonField('owner_id', Snowflake, str),
    permissions=JsonField('permissions'),
    region=JsonField('region'),
    afk_channel_id=JsonField('afk_channel_id', Snowflake, str),
    afk_timeout=JsonField('afk_timeout'),
    verification_level=JsonField('verification_level'),
    default_message_notifications=JsonField('default_message_notifications'),
    explicit_content_filter=JsonField('explicit_content_filter'),
    mfa_level=JsonField('mfa_level'),
    application_id=JsonField('application_id', Snowflake, str),
    system_channel_id=JsonField('system_channel_id', Snowflake, str),
    system_channel_flags=JsonField('system_channel_flags'),
    rules_channel_id=JsonField('rules_channel_id', Snowflake, str),
    joined_at=JsonField('joined_at'),
    large=JsonField('large'),
    unavailable=JsonField('unavailable'),
    member_count=JsonField('member_count'),
    _voice_states=JsonArray('voice_states'),
    _threads=JsonArray('threads'),
    _presences=JsonArray('presences'),
    max_presences=JsonField('max_presences'),
    max_members=JsonField('max_members'),
    banner=JsonField('banner'),
    premium_tier=JsonField('permium_tier'),
    premium_subscription_count=JsonField('premium_subscription_count'),
    preferred_locale=JsonField('preferred_locale'),
    public_updates_channel_id=JsonField(
        'public_updates_channel_id', Snowflake, str
    ),
    max_video_channel_users=JsonField('max_video_channel_users'),
    nsfw=JsonField('nsfw'),
    __extends__=(GuildPreviewTemplate,)
)


class Guild(BaseObject, template=GuildTemplate):
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
    # TODO(asleep-cult): Do it
    __slots__ = ('widget', 'vanity_url', 'welcome_screen', 'channels',
                 'emojis', 'roles', 'members')

    def __init__(self, *, state):
        super().__init__(state=state)

        self.widget = GuildWidget.unmarshal(guild=self)
        self.vanity_url = GuildVanityURL.unmarshal(guild=self)
        self.welcome_screen = WelcomeScreen.unmarshal(guild=self)

        self.channels = self.state.manager.get_class('GuildChannelState')(
            superstate=self.state.manager.channels,
            guild=self)

        self.emojis = self.state.manager.get_class('GuildEmojiState')(
            manager=self.state.manager,
            guild=self)

        self.roles = self.state.manager.get_class('RoleState')(
            manager=self.state.manager,
            guild=self)

        self.members = self.state.manager.get_class('GuildMemberState')(
            manager=self.state.manager,
            guild=self)

    async def modify(self, **kwargs):
        keys = rest.modify_guild.keys

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.id),
            json=kwargs)

        return self.state.upsert(data)

    async def delete(self):
        await rest.delete_guild.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.id))

    async def prune(self, **kwargs):
        remove = kwargs.pop('remove', True)

        if remove:
            keys = rest.begin_guild_prune.json
        else:
            keys = rest.get_guild_prune_count.params

        try:
            roles = Snowflake.try_snowflake_set(kwargs['roles'])

            if remove:
                kwargs['include_roles'] = tuple(roles)
            else:
                kwargs['include_roles'] = ','.join(map(str, roles))
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.prune',
                       kwargs, (), keys)

        if remove:
            data = await rest.begin_guild_prune.request(
                session=self.state.manager.rest,
                fmt=dict(guild_id=self.id),
                json=kwargs)
        else:
            data = await rest.get_guild_prune_count.request(
                session=self.state.manager.rest,
                fmt=dict(guild_id=self.id),
                params=kwargs)

        return data['pruned']

    async def preview(self):
        return await self.state.fetch_preview(self.id)

    async def voice_regions(self):
        data = await rest.get_guild_voice_regions.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.id))

        return data

    async def invites(self):
        data = await rest.get_guild_invites.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.id))

        return self.state.manager.upsert_many(data)

    async def templates(self):
        data = await rest.get_guild_templates.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.id))

        return self.state.new_template_many(data)

    async def create_template(self, **kwargs):
        required_keys = ('name',)
        keys = rest.create_guild_template.json

        _validate_keys(f'{self.__class__.__name__}.create_template',
                       kwargs, required_keys, keys)

        data = await rest.create_guild_template.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.id),
            json=kwargs)

        return self.state.new_template(data)

    def to_preview_dict(self):
        return GuildPreviewTemplate.to_dict(self)

    def _update_emojis(self, emojis):
        emojis = self.emojis.upsert_many(emojis)
        for emoji in set(self.emojis):
            if emoji not in emojis:
                self.emojis.pop(emoji.id)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        widget_data = {}

        widget_channel_id = data.get('widget_channel_id')
        if widget_channel_id is not None:
            widget_data['channel_id'] = widget_channel_id

        widget_enabled = data.get('widget_enabled')
        if widget_enabled is not None:
            widget_data['enabled'] = widget_enabled

        if widget_data:
            self.widget.update(data)

        vanity_url_code = data.get('vanity_url_code')
        if vanity_url_code is None:
            self.vanity_url.update({'code': vanity_url_code})

        channels = data.get('channels')
        if channels is not None:
            for channel in channels:
                channel = self.state.manager.channels.upsert(channel)
                self.channels.add_key(channel.id)

        emojis = data.get('emojis')
        if emojis is not None:
            self._update_emojis(emojis)

        roles = data.get('roles')
        if roles is not None:
            self.roles.upsert_many(roles)

        members = data.get('members')
        if members is not None:
            self.members.upsert_many(members)

        welcome_screen = data.get('welcome_screen')
        if welcome_screen is not None:
            self.welcome_screen.update(data)


GuildBanTemplate = JsonTemplate(
    reason=JsonField('reason'),
)


class GuildBan(BaseObject, template=GuildBanTemplate):
    __slots__ = ('guild', 'user')

    def __init__(self, *, state, guild):
        super().__init__(state)
        self.guild = guild

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.manager.users.upsert(user)
            self.id = self.user.id


WelcomeScreenChannelTemplate = JsonTemplate(
    channel_id=JsonField('channel_id', Snowflake, str),
    description=JsonField('description'),
    enoji_id=JsonField('emoji', Snowflake, str),
    emoji_name=JsonField('emoji_name'),
)


class WelcomeScreenChannel(JsonObject, template=WelcomeScreenChannelTemplate):
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
    __slots__ = ('guild',)

    def __init__(self, *, welcome_screen):
        self.welcome_screen = welcome_screen

    @property
    def channel(self):
        """The channel that this welcome channel refers to

        warning:
            This property relies on the channel cache so it could return None
        """
        return self.welcome_screen.guild.channels.get(self.id)

    @property
    def emoji(self):
        """The welcome channel's emoji

        warning:
            This property relies on the emoji cache to it could return None
        """
        return self.guild.emojis.get(self.emoji_id)


WelcomeScreenTemplate = JsonTemplate(
    description=JsonField('description'),
)


class WelcomeScreen(JsonObject, template=WelcomeScreenTemplate):
    """Represents a `Guild`'s welcome screen

    Attributes:
        description str: The welcome screen's description

        guild Guild: The guild associated with the welcome screen

        welcome_channels list[WelcomeChannel]: The welcome screen's channels
    """
    __slots__ = ('guild', 'welcome_channels')

    def __init__(self, *, guild):
        self.guild = guild
        self.welcome_channels = []

    async def fetch(self):
        """Invokes an API request to get the welcome screen

        Returns:
            WelcomeScreen: The updated welcome screen
        """
        data = await rest.get_guild_welcome_screen.request(
            session=self.guild.state.manager.rest,
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
        welcome_channel_keys = WelcomeScreenChannelTemplate.fields

        try:
            welcome_channels = []

            for key, value in kwargs['welcome_channels'].items():
                value['channel_id'] = Snowflake.try_snowflake(key)

                try:
                    emoji = value['emoji']
                    value['emoji_id'] = emoji.id
                    value['emoji_name'] = emoji.name
                except KeyError:
                    pass

                _validate_keys(f'welcome_channels[{key}]',
                               value, (), welcome_channel_keys)

                welcome_channels.append(value)
        except KeyError:
            pass

        keys = rest.modify_guild_welcome_screen.json

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild_welcome_screen.request(
            session=self.guild.state.manager.rest,
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
                channel = WelcomeScreenChannel.unmarshal(
                    channel, guild=self.guild)
                self.welcome_channels.append(channel)
