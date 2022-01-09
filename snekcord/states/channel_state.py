from .base_state import BaseSate
from ..exceptions import UnknownModelError
from ..models import (
    BaseChannel,
    CategoryChannel,
    ChannelType,
    GuildChannel,
    ModelWrapper,
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

        if isinstance(object, ModelWrapper):
            if isinstance(object.state, cls):
                return object.id

            raise TypeError('Expected ModelWrapper created by ChannelState')

        raise TypeError('Expected Snowflake, str, int, BaseChannelModel or ModelWrapper')

    def get_model(self, type):
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
        except UnknownModelError:
            model = self.get_model(ChannelType(data['type']))
            channel = model.unmarshal(data, state=self)
        else:
            channel.update(data)

        if isinstance(channel, GuildChannel):
            guild_id = data.get('guild_id')
            if guild_id is not None:
                channel.guild.set_id(guild_id)

        return channel
