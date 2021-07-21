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
    banner_id = JsonField('banner_id', Snowflake)

    def __init__(self, *, state):
        self.state = state
        self.sticker_ids = set()

    def get_stickers(self):
        yield from self.state.get_all(self.sticker_ids)

    def update(self, data):
        super().update(data)

        if 'stickers' in data:
            for sticker in data:
                self.sticker_ids.add(self.state.upsert(sticker).id)

        return self


class Sticker(BaseObject):
    __slots__ = ('creator',)

    description = JsonField('description')
    type = JsonField('type', StickerType.get_enum)
    format = JsonField('format_type', StickerFormatType.get_enum)
    name = JsonField('name')
    pack_id = JsonField('pack_id', Snowflake)
    tags = JsonField('tags', lambda tags: tags.split(', '))
    available = JsonField('available')
    guild_id = JsonField('guild_id')
    sort_value = JsonField('sort_value')

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

    async def modify(self, *, name=None, description=undefined, tags=None):
        json = {}

        if name is not None:
            json['name'] = str(name)

        if description is not undefined:
            if description is not None:
                json['description'] = str(description)
            else:
                json['description'] = None

        if tags is not None:
            json['tags'] = [str(tag) for tag in tags]

        data = await rest.modify_guild_sticker.request(
            self.state.client.rest,
            {'guild_id': self.guild.id, 'sticker_id': self.id},
            json=json
        )

        return self.state.upsert(data)

    def delete(self):
        return self.state.delete(self.id)

    def _delete(self):
        super()._delete()

        if self.guild is not None:
            self.guild.stickers.remove_key(self.id)

    def update(self, data):
        super().update(data)

        if 'user' in data:
            self.creator = self.state.client.users.upsert(data['user'])

        return self
