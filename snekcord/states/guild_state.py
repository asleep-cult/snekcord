from .base_state import BaseSate
from ..exceptions import UnknownModelError
from ..models import (
    Guild,
    ModelWrapper,
)
from ..rest.endpoints import (
    GET_GUILD,
)
from ..snowflake import Snowflake

__all__ = ('GuildState',)


class GuildState(BaseSate):
    @classmethod
    def unwrap_id(cls, object):
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (int, str)):
            return Snowflake(object)

        if isinstance(object, Guild):
            return object.id

        if isinstance(object, ModelWrapper):
            if isinstance(object.state, cls):
                return object

            raise TypeError('Expected ModelWrapper created by GuildState')

        raise TypeError('Expected Snowflake, int, str, GuildModel or ModelWrapper')

    async def upsert(self, data):
        try:
            guild = self.get(data['id'])
        except UnknownModelError:
            guild = Guild.unmarshal(data, state=self)
        else:
            guild.update(data)

        owner_id = data.get('owner_id')
        if owner_id is not None:
            guild.owner.set_id(owner_id)

        if 'widget_channel_id' in data:
            guild.widget_channel.set_id(data['widget_channel_id'])

        if 'system_channel_id' in data:
            guild.system_channel.set_id(data['system_channel_id'])

        if 'rules_channel_id' in data:
            guild.rules_channel.set_id(data['rules_channel_id'])

        roles = data.get('roles')
        if roles is not None:
            await guild._update_roles(roles)

        members = data.get('members')
        if members is not None:
            # await guild._update_members(members)
            pass

        emojis = data.get('emojis')
        if emojis is not None:
            await guild._update_emojis(emojis)

        channels = data.get('channels')
        if channels is not None:
            await guild._update_channels(channels)

        return guild

    async def fetch(self, guild):
        guild_id = self.unwrap_id(guild)

        data = await self.client.rest.request(GET_GUILD, guild_id=guild_id)
        assert isinstance(data, dict)

        return await self.upsert(data)
