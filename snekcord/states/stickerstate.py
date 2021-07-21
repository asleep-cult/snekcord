from .basestate import BaseState, BaseSubState
from .. import rest
from ..clients.client import ClientClasses
from ..resolvers import resolve_image_data
from ..utils import Snowflake


class StickerState(BaseState):
    def upsert(self, data):
        sticker = self.get(Snowflake(data['id']))

        if sticker is not None:
            sticker.update(data)
        else:
            sticker = ClientClasses.Sticker.unmarshal(data, state=self)
            sticker.cache()

        return sticker

    def new_pack(self, data):
        return ClientClasses.StickerPack.unmarshal(data, state=self)

    async def fetch(self, sticker):
        sticker_id = Snowflake.try_snowflake(sticker)

        data = await rest.get_sticker.request(
            self.client.rest, {'sticker_id': sticker_id}
        )

        return self.upsert(data)

    async def fetch_packs(self):
        data = await rest.get_sticker_packs.request(self.client.rest)

        return [self.new_pack(pack) for pack in data]


class GuildStickerState(BaseSubState):
    def __init__(self, *, superstate, guild):
        super().__init__(superstate=superstate)
        self.guild = guild

    def upsert(self, data):
        sticker = self.superstate.upsert(data)
        sticker._json_data_['guild_id'] = self.guild._json_data_['guild_id']

        self.add_key(sticker.id)

        return sticker

    async def fetch(self, sticker):
        sticker_id = Snowflake.try_snowflake(sticker)

        data = await rest.get_guild_sticker.request(
            self.superstate.client.rest,
            {'guild_id': self.guild.id, 'sticker_id': sticker_id}
        )

        return self.upsert(data)

    async def fetch_all(self):
        data = await rest.get_guild_stickers.request(
            self.superstate.client.rest, {'guild_id': self.guild.id}
        )

        return [self.upsert(sticker) for sticker in data]

    async def create(self, *, name, image, tags, description=None):
        json = {'name': str(name)}

        json['image'] = await resolve_image_data(image)
        json['tags'] = [str(tag) for tag in tags]

        if description is not None:
            json['description'] = description

        data = await rest.create_guild_sticker.request(
            self.superstate.client.rest, {'guild_id': self.guild.id}, json=json
        )

        return self.upsert(data)

    async def delete(self, sticker):
        sticker_id = Snowflake.try_snowflake(sticker)

        await rest.delete_guild_sticker.request(
            self.superstate.client.rest,
            {'guild_id': self.guild.id, 'sticker_id': sticker_id}
        )
