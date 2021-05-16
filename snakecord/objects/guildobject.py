from .baseobject import BaseObject
from .inviteobject import GuildVanityUrl
from .widgetobject import GuildWidget
from .. import rest
from ..templates import GuildBanTemplate, GuildPreviewTemplate, GuildTemplate
from ..utils import Snowflake, _validate_keys


class Guild(BaseObject, template=GuildTemplate):
    __slots__ = ('widget', 'vanity_url', 'channels')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.widget = GuildWidget(owner=self)
        self.vanity_url = GuildVanityUrl(owner=self)

        GuildChannelState = self.state.manager.get_class('GuildChannelState')
        self.channels = GuildChannelState(
                superstate=self.state.manager.channels,
                guild=self)

    async def modify(self, **kwargs):
        keys = rest.modify_guild.keys

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.id),
            json=kwargs)

        return self.append(data)

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

    async def fetch_preview(self):
        return await self.state.fetch_preview(self.id)

    async def fetch_voice_regions(self):
        data = await rest.get_guild_voice_regions.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.id))

        return data

    def to_preview_dict(self):
        return GuildPreviewTemplate.to_dict(self)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        widget_channel_id = data.get('widget_channel_id')
        if widget_channel_id is not None:
            self.widget.channel_id = widget_channel_id

        widget_enabled = data.get('widget_enabled')
        if widget_enabled is not None:
            self.widget.enabled = widget_enabled

        vanity_url_code = data.get('vanity_url_code')
        if vanity_url_code is None:
            self.vanity_url.code = vanity_url_code

        channels = data.get('channels')
        if channels is not None:
            for channel in channels:
                channel = self.state.manager.channels.append(
                    channel, guild=self)
                self.channels.add_key(channel.id)


class GuildBan(BaseObject, template=GuildBanTemplate):
    __slots__ = ('guild', 'user')

    def __init__(self, *, state, guild):
        super().__init__(state)
        self.guild = guild

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.manager.users.append(user)
            self.id = self.user.id
