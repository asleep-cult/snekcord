from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..enums import ExplicitContentFilterLevel, MessageNotificationsLevel
from ..flags import SystemChannelFlags
from ..resolvers import resolve_data_uri
from ..utils import Snowflake

__all__ = ('GuildState', 'GuildBanState')


class GuildState(BaseState):
    def upsert(self, data):
        guild = self.get(Snowflake(data['id']))

        if guild is not None:
            guild.update(data)
        else:
            guild = ClientClasses.Guild.unmarshal(data, state=self)
            guild.cache()

        return guild

    def new_template(self, data):
        return ClientClasses.GuildTemplate.unmarshal(data, state=self)

    async def fetch(self, guild, *, with_counts=None, sync=True):
        guild_id = Snowflake.try_snowflake(guild)

        params = {}

        if with_counts is not None:
            params['with_counts'] = with_counts

        data = await rest.get_guild.request(self.client.rest, guild_id=guild_id)

        guild = self.upsert(data)

        if sync:
            await guild.sync(data)

        return guild

    async def fetch_many(self, *, before=None, after=None, limit=None, sync=True):
        params = {}

        if before is not None:
            params['before'] = Snowflake.try_snowflake(before, allow_datetime=True)

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after, allow_datetime=True)

        if limit is not None:
            params['limit'] = int(limit)

        data = await rest.get_my_guilds.request(self.client.rest)

        guilds = [self.upsert(guild) for guild in data]

        if sync:
            for guild in guilds:
                await guild.sync(data)

        return guilds

    async def fetch_preview(self, guild):
        guild_id = Snowflake.try_snowflake(guild)

        data = await rest.get_guild_preview.request(
            self.client.rest, guild_id=guild_id
        )

        return self.upsert(data)

    async def fetch_template(self, code):
        data = await rest.get_template.request(
            self.client.rest, template_code=code
        )

        return self.new_template(data)

    async def create(
        self, *, name, icon=None, verification_level=None, default_message_notifications=None,
        explicit_content_filter=None,  # roles, channels, afk_channel_id, system_channel_id
        afk_timeout=None, system_channel_flags=None,
    ):
        json = {'name': str(name)}

        if icon is not None:
            json['icon'] = await resolve_data_uri(icon)

        if verification_level is not None:
            json['default_message_notifications'] = (
                MessageNotificationsLevel.get_value(default_message_notifications)
            )

        if explicit_content_filter is not None:
            json['explicit_content_filter'] = (
                ExplicitContentFilterLevel.get_value(explicit_content_filter)
            )

        if afk_timeout is not None:
            json['afk_timeout'] = int(afk_timeout)

        if system_channel_flags is not None:
            json['system_channel_flags'] = SystemChannelFlags.get_value(system_channel_flags)

        data = await rest.create_guild.request(self.client.rest, json=json)

        return self.upsert(data)

    async def leave(self, guild):
        guild_id = Snowflake.try_snowflake(guild)

        await rest.leave_guild.request(
            self.client.rest, guild_id=guild_id
        )

    async def delete(self, guild):
        guild_id = Snowflake.try_snowflake(guild)

        await rest.delete_guild.request(
            self.client.rest, guild_id=guild_id
        )


class GuildBanState(BaseState):
    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data):
        ban = self.get(Snowflake(data['user']['id']))

        if ban is not None:
            ban.update(data)
        else:
            ban = ClientClasses.GuildBan.unmarshal(data, state=self)
            ban.cache()

        return ban

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_guild_ban.request(
            self.client.rest, guild_id=self.guild.id, user_id=user_id
        )

        return self.upsert(data)

    async def fetch_all(self):
        data = await rest.get_guild_bans.request(
            self.client.rest, guild_id=self.guild.id
        )

        return [self.upsert(ban) for ban in data]

    async def add(self, user, *, delete_message_days=None, reason=None):
        json = {}

        if delete_message_days is not None:
            json['delete_message_days'] = int(delete_message_days)

        if reason is not None:
            json['reason'] = str(reason)

        user_id = Snowflake.try_snowflake(user)

        await rest.create_guild_ban.request(
            self.client.rest, guild_id=self.guild.id, user_id=user_id
        )

    async def remove(self, user):
        user_id = Snowflake.try_snowflake(user)

        await rest.remove_guild_ban.request(
            self.client.rest, guild_id=self.guild.id, user_id=user_id
        )
