from datetime import datetime

from ..utils import (
    JsonArray,
    JsonField,
    JsonObject,
    JsonTemplate,
    _validate_keys,
)

__all__ = (
    'EmbedThumbnail',
    'EmbedVideo',
    'EmbedImage',
    'EmbedProvider',
    'EmbedAuthor',
    'EmbedFooter',
    'EmbedField',
    'Embed',
)

EmbedThumbnail = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width'),
).default_object('EmbedThumbnail')


EmbedVideo = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width'),
).default_object('EmbedVideo')


EmbedImage = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width'),
).default_object('EmbedImage')


EmbedProvider = JsonTemplate(
    name=JsonField('name'), url=JsonField('url')
).default_object('EmbedProvider')


EmbedAuthor = JsonTemplate(
    name=JsonField('name'),
    url=JsonField('url'),
    icon_url=JsonField('icon_url'),
    proxy_icon_url=JsonField('proxy_icon_url'),
).default_object('EmbedAuthor')


EmbedFooter = JsonTemplate(
    text=JsonField('text'),
    icon_url=JsonField('icon_url'),
    proxy_icon_url=JsonField('proxy_icon_url'),
).default_object('EmbedFooter')


EmbedField = JsonTemplate(
    name=JsonField('name'), value=JsonField('value'), inline=JsonField('inline')
).default_object('EmbedField')


EmbedTemplate = JsonTemplate(
    title=JsonField('title'),
    type=JsonField('type'),
    description=JsonField('description'),
    url=JsonField('url'),
    timestamp=JsonField(
        'timestamp', datetime.fromisoformat, datetime.isoformat
    ),
    color=JsonField('color'),
    footer=JsonField('footer', object=EmbedFooter),
    image=JsonField('image', object=EmbedImage),
    thumbnail=JsonField('thumbnail', object=EmbedThumbnail),
    video=JsonField('video', object=EmbedVideo),
    provider=JsonField('provider', object=EmbedProvider),
    author=JsonField('author', object=EmbedAuthor),
    fields=JsonArray('fields', object=EmbedField),
)


class Embed(JsonObject, template=EmbedTemplate):
    def __init__(self, **kwargs):
        keys = ('title', 'type', 'description', 'url', 'timestamp', 'color')

        _validate_keys(f'{self.__class__.__name__}.__init__', kwargs, (), keys)

        self.update(kwargs)

    @property
    def colour(self):
        return self.color

    @colour.setter
    def colour(self, value):
        self.color = value

    def add_field(self, **kwargs):
        required_keys = ('name', 'value')
        keys = EmbedField.fields

        _validate_keys(
            f'{self.__class__.__name__}.add_field', kwargs, required_keys, keys
        )

        self.fields.append(EmbedField.unmarshal(kwargs))
