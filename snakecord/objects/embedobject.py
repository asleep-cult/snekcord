from datetime import datetime

from ..utils import JsonArray, JsonField, JsonObject, JsonTemplate

EmbedThumbnailTemplate = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width')
)

EmbedThumnail = EmbedThumbnailTemplate.default_object('EmbedThumbnail')

EmbedVideoTemplate = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width')
)

EmbedVideo = EmbedVideoTemplate.default_object('EmbedVideo')

EmbedImageTemplate = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width')
)

EmbedImage = EmbedImageTemplate.default_object('EmbedImage')

EmbedProviderTemplate = JsonTemplate(
    name=JsonField('name'),
    url=JsonField('url')
)

EmbedProvider = EmbedProviderTemplate.default_object('EmbedProvider')

EmbedAuthorTemplate = JsonTemplate(
    name=JsonField('name'),
    url=JsonField('url'),
    icon_url=JsonField('icon_url'),
    proxy_icon_url=JsonField('proxy_icon_url')
)

EmbedAuthor = EmbedAuthorTemplate.default_object('EmbedAuthor')

EmbedFooterTemplate = JsonTemplate(
    text=JsonField('text'),
    icon_url=JsonField('icon_url'),
    proxy_icon_url=JsonField('proxy_icon_url')
)

EmbedFooter = EmbedFooterTemplate.default_object('EmbedFooter')

EmbedFieldTemplate = JsonTemplate(
    name=JsonField('name'),
    value=JsonField('value'),
    inline=JsonField('inline')
)

EmbedField = EmbedFieldTemplate.default_object('EmbedField')

EmbedTemplate = JsonTemplate(
    title=JsonField('title'),
    type=JsonField('type'),
    description=JsonField('description'),
    url=JsonField('url'),
    timestamp=JsonField('timestamp', unmarshal=datetime.fromisoformat),
    color=JsonField('color'),
    footer=JsonField('footer', object=EmbedFooter),
    image=JsonField('image', object=EmbedImage),
    thumbnail=JsonField('thumbnail', object=EmbedThumnail),
    video=JsonField('video', object=EmbedVideo),
    provider=JsonField('provider', object=EmbedProvider),
    author=JsonField('author', object=EmbedAuthor),
    fields=JsonArray('fields', object=EmbedField)
)

class Embed(JsonObject, template=EmbedTemplate):
    def __init__(self, **kwargs):
        self.title = kwargs.get('title')
        self.type = kwargs.get('type')
        self.description = kwargs.get('description')
        self.url = kwargs.get('url')
        self.timestamp = kwargs.get('timestamp')
        self.color = kwargs.get('color')
    
    @property
    def colour(self):
        return self.color

    @colour.setter
    def colour(self, value):
        self.color = value
    
    def add_field(self, name, value, inline=True):
        self.fields.append(
            EmbedField.unmarshal(dict(name=name, value=value, inline=inline))
        )

    def insert_field(self, index, name, value, inline=True):
        self.fields.insert(
            index, EmbedField.unmarshal(dict(name=name, value=value, inline=inline))
        )
