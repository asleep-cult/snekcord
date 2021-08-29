from .basestate import BaseState, BaseSubState
from .. import http
from ..enums import StickerType
from ..objects.stickerobject import GuildSticker, StandardSticker, StickerPack
from ..resolvers import resolve_data, resolve_mimetype
from ..snowflake import Snowflake


class StickerState(BaseState):
    def get_class(self, type):
        if type == StickerType.GUILD:
            return GuildSticker
        elif type == StickerType.STANDARD:
            return StandardSticker

    def upsert(self, data):
        sticker = self.get(Snowflake(data['id']))

        if sticker is not None:
            sticker.update(data)
        else:
            sticker = self.get_class(data['type']).unmarshal(data, state=self)
            sticker.cache()

        return sticker

    def new_pack(self, data):
        return StickerPack.unmarshal(data, state=self)

    async def fetch(self, sticker):
        sticker_id = Snowflake.try_snowflake(sticker)

        data = await http.get_sticker.request(
            self.client.http, sticker_id=sticker_id
        )

        return self.upsert(data)

    async def fetch_packs(self):
        data = await http.get_sticker_packs.request(self.client.http)

        return [self.new_pack(pack) for pack in data['sticker_packs']]


class GuildStickerState(BaseSubState):
    def __init__(self, *, superstate, guild):
        super().__init__(superstate=superstate)
        self.guild = guild

    def upsert(self, data):
        sticker = self.superstate.upsert(data)
        sticker._json_data_['guild_id'] = self.guild._json_data_['id']

        self.add_key(sticker.id)

        return sticker

    async def fetch(self, sticker):
        sticker_id = Snowflake.try_snowflake(sticker)

        data = await http.get_guild_sticker.request(
            self.superstate.client.http, guild_id=self.guild.id, sticker_id=sticker_id
        )

        return self.upsert(data)

    async def fetch_all(self):
        data = await http.get_guild_stickers.request(
            self.superstate.client.http, guild_id=self.guild.id
        )

        return [self.upsert(sticker) for sticker in data]

    async def create(self, *, name, image, tag, description=None):
        data = {}

        data['name'] = str(name)
        data['tags'] = str(tag)

        if description is not None:
            data['description'] = str(description)
        else:
            data['description'] = ''

        image = await resolve_data(image)
        mimetype, ext = resolve_mimetype(image)

        data = await http.create_guild_sticker.request(
            self.superstate.client.http, guild_id=self.guild.id,
            data=data, files={'file': (f'file{ext}', image, mimetype)},
        )

        return self.upsert(data)

    async def delete(self, sticker):
        sticker_id = Snowflake.try_snowflake(sticker)

        await http.delete_guild_sticker.request(
            self.superstate.client.http, guild_id=self.guild.id, sticker_id=sticker_id
        )
