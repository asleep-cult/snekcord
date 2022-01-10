from .base_state import BaseSate
from ..exceptions import UnknownObjectError
from ..objects import (
    BaseChannel,
    CategoryChannel,
    ChannelType,
    GuildChannel,
    ObjectWrapper,
    StoreChannel,
    TextChannel,
    VoiceChannel,
)
from ..snowflake import Snowflake

__all__ = ('ChannelState',)


class ChannelState(BaseSate):
    @classmethod
    def unwrap_id(cls, object) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (str, int)):
            return Snowflake(object)

        if isinstance(object, BaseChannel):
            return object.id

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, cls):
                return object.id

            raise TypeError('Expected ObjectWrapper created by ChannelState')

        raise TypeError('Expected Snowflake, str, int, BaseChannel or ObjectWrapper')

    def get_object(self, type):
        if type is ChannelType.GUILD_CATEGORY:
            return CategoryChannel

        if type is ChannelType.GUILD_STORE:
            return StoreChannel

        if type is ChannelType.GUILD_TEXT:
            return TextChannel

        if type is ChannelType.GUILD_VOICE:
            return VoiceChannel

        return BaseChannel

    async def upsert(self, data):
        try:
            channel = self.get(data['id'])
        except UnknownObjectError:
            object = self.get_object(ChannelType(data['type']))
            channel = object.unmarshal(data, state=self)
        else:
            channel.update(data)

        if isinstance(channel, GuildChannel):
            guild_id = data.get('guild_id')
            if guild_id is not None:
                channel.guild.set_id(guild_id)

        return channel
