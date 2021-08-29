from .baseobject import BaseObject
from .. import http
from ..enums import StickerFormatType, StickerType
from ..json import JsonField, JsonObject
from ..snowflake import Snowflake
from ..undefined import undefined


class StickerPack(JsonObject):
    id = JsonField('id', Snowflake)
    name = JsonField('name')
    sku_id = JsonField('sku_id', Snowflake)
    cover_sticker_id = JsonField('cover_sticker_id', Snowflake)
    description = JsonField('description')
    banner_asset_id = JsonField('banner_asset_id', Snowflake)

    def __init__(self, *, state):
        self.state = state
        self.stickers = []

    def update(self, data):
        super().update(data)

        if 'stickers' in data:
            self.stickers.clear()

            for sticker in data['stickers']:
                self.stickers.append(self.state.upsert(sticker))

        return self


class StickerItem(JsonObject):
    id = JsonField('id', Snowflake)
    name = JsonField('name')
    format = JsonField('format_type', StickerFormatType.try_enum)

    def __init__(self, *, state):
        self.state = state

    @property
    def sticker(self):
        return self.state.get(self.id)

    def fetch_sticker(self):
        return self.state.fetch(self.id)


class _BaseSticker(BaseObject):
    name = JsonField('name')
    description = JsonField('description')
    type = JsonField('type', StickerType.try_enum)
    format = JsonField('format_type', StickerFormatType.try_enum)

    def __str__(self):
        return f':{self.tag}:'


class StandardSticker(_BaseSticker):
    pack_id = JsonField('pack_id', Snowflake)
    tags = JsonField('tags', lambda tags: tags.split(', '))
    sort_value = JsonField('sort_value')

    @property
    def tag(self):
        return self.tags[0]


class GuildSticker(_BaseSticker):
    __slots__ = ('creator',)

    tag = JsonField('tags')
    available = JsonField('available')
    guild_id = JsonField('guild_id', Snowflake)

    def __init__(self, *, state):
        super().__init__(state=state)
        self.creator = None

    @property
    def guild(self):
        return self.state.client.guilds.get(GuildSticker.guild_id.get(self))

    async def fetch_guild(self):
        if self.guild is not None:
            return await self.guild.fetch()

        data = await http.get_sticker_guild.request(
            self.state.client.http, sticker_id=self.id
        )

        guild = self.state.client.guilds.upsert(data)
        self._json_data_['guild_id'] = guild._json_data_['id']
        return guild

    async def modify(self, *, name=None, description=undefined, tag=None):
        json = {}

        if name is not None:
            json['name'] = str(name)

        if description is not undefined:
            if description is not None:
                json['description'] = str(description)
            else:
                json['description'] = None

        if tag is not None:
            json['tags'] = str(tag)

        data = await http.modify_guild_sticker.request(
            self.state.client.http, guild_id=self.guild.id, sticker_id=self.id, json=json
        )

        return self.state.upsert(data)

    def delete(self):
        return self.guild.stickers.delete(self.id)

    def _delete(self):
        super()._delete()

        if self.guild is not None:
            self.guild.stickers.remove_key(self.id)

    def update(self, data):
        super().update(data)

        if 'user' in data:
            self.creator = self.state.client.users.upsert(data['user'])

        return self
