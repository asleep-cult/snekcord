from .base_state import BaseSate
from ..exceptions import UnknownModelError
from ..models import (
    CustomEmojiModel,
    ModelWrapper,
)
from ..rest.endpoints import (
    GET_GUILD_EMOJI,
    GET_GUILD_EMOJIS,
)
from ..snowflake import Snowflake

__all__ = ('EmojiState',)


class EmojiState(BaseSate):
    def __init__(self, *, client, guild) -> None:
        super().__init__(client=client)
        self.guild = guild

    @classmethod
    def unwrap_id(cls, object):
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (str, int)):
            return Snowflake(object)

        if isinstance(object, CustomEmojiModel):
            return object.id

        if isinstance(object, ModelWrapper):
            if isinstance(object.state, cls):
                return object.id

            raise TypeError('Expected ModelWrapper created by EmojiState')

        raise TypeError('Expected Snowflake, str, int. CustomEmojiModel or ModelWrapper')

    async def upsert(self, data):
        user = data.get('user')
        if user is not None:
            user = await self.client.users.upsert(user)

        try:
            emoji = self.get(data['id'])
        except UnknownModelError:
            emoji = CustomEmojiModel.unmarshal(data, state=self, user=user)
        else:
            emoji.update(data)
            emoji.user = user

        roles = data.get('roles')
        if roles is not None:
            emoji._update_roles(roles)

        return emoji

    async def fetch(self, emoji):
        emoji_id = self.unwrap_id(emoji)

        data = await self.client.request(
            GET_GUILD_EMOJI, guild_id=self.guild.id, emoji_id=emoji_id
        )
        assert isinstance(data, dict)

        return await self.upsert(data)

    async def fetch_all(self):
        data = await self.client.request(GET_GUILD_EMOJIS, guild_id=self.guild.id)
        assert isinstance(data, list)

        return [await self.upsert(emoji) for emoji in data]
