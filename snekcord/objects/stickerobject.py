from .baseobject import BaseObject
from .. import rest
from ..enums import StickerFormatType, StickerType
from ..exceptions import PartialObjectError
from ..utils import JsonField, JsonObject, Snowflake, undefined


class StickerPack(JsonObject):
    id = JsonField('id', Snowflake)
    name = JsonField('name')
    sku_id = JsonField('sku_id', Snowflake)
    cover_sticker_id = JsonField('cover_sticker_id', Snowflake)
    description = JsonField('description')
    banner_asset_id = JsonField('banner_asset_id', Snowflake)

    def __init__(self, *, state):
        self.state = state
        self.sticker_ids = []

    def get_stickers(self):
        yield from self.state.client.stickers.get_all(self.sticker_ids)

    def update(self, data):
        super().update(data)

        if 'stickers' in data:
            self.sticker_ids.clear()

            for sticker in data['stickers']:
                self.sticker_ids.append(self.state.client.stickers.upsert(sticker).id)

        return self


class StickerItem(JsonObject):
    id = JsonField('id', Snowflake)
    name = JsonField('name')
    format = JsonField('format_type', StickerFormatType.get_enum)

    def __init__(self, *, state):
        self.state = state

    @property
    def sticker(self):
        return self.state.get(self.id)


class _BaseSticker(BaseObject):
    name = JsonField('name')
    description = JsonField('description')
    type = JsonField('type', StickerType.get_enum)
    format = JsonField('format', StickerFormatType.get_enum)


class StandardSticker(_BaseSticker):
    pack_id = JsonField('pack_id', Snowflake)
    tags = JsonField('tags', lambda tags: tags.split(', '))
    sort_value = JsonField('sort_value')


class GuildSticker(_BaseSticker):
    __slots__ = ('creator',)

    tags = JsonField('tags')
    available = JsonField('available')
    guild_id = JsonField('guild_id', Snowflake)

    def __init__(self, *, state):
        super().__init__(state=state)
        self.creator = None

    @property
    def guild(self):
        try:
            return self.state.client.guilds.get(self.guild_id)
        except PartialObjectError:
            return None

    async def fetch_guild(self):
        if self.guild is not None:
            return await self.guild.fetch()

        data = await rest.get_sticker_guild.request(
            self.state.client.rest, {'sticker_id': self.id}
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

        data = await rest.modify_guild_sticker.request(
            self.state.client.rest,
            {'guild_id': self.guild.id, 'sticker_id': self.id},
            json=json
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
