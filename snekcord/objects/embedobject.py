import copy
import enum
import operator
from datetime import datetime

from ..utils import (JsonArray, JsonField, JsonObject, JsonTemplate)

__all__ = ('EmbedType', 'EmbedThumbnail', 'EmbedVideo', 'EmbedImage',
           'EmbedProvider', 'EmbedAuthor', 'EmbedFooter', 'EmbedField',
           'Embed', 'EmbedBuilder')


class EmbedType(enum.Enum):
    RICH = 'rich'
    IMAGE = 'image'
    VIDEO = 'video'
    GIFV = 'gifv'
    ARTICLE = 'article'
    LINK = 'link'


EmbedThumbnail = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width')
).default_object('EmbedThumbnail')


EmbedVideo = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width')
).default_object('EmbedVideo')


EmbedImage = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width')
).default_object('EmbedImage')


EmbedProvider = JsonTemplate(
    name=JsonField('name'),
    url=JsonField('url')
).default_object('EmbedProvider')


EmbedAuthor = JsonTemplate(
    name=JsonField('name'),
    url=JsonField('url'),
    icon_url=JsonField('icon_url'),
    proxy_icon_url=JsonField('proxy_icon_url')
).default_object('EmbedAuthor')


EmbedFooter = JsonTemplate(
    text=JsonField('text'),
    icon_url=JsonField('icon_url'),
    proxy_icon_url=JsonField('proxy_icon_url')
).default_object('EmbedFooter')


EmbedField = JsonTemplate(
    name=JsonField('name'),
    value=JsonField('value'),
    inline=JsonField('inline')
).default_object('EmbedField')


EmbedTemplate = JsonTemplate(
    title=JsonField('title'),
    type=JsonField(
        'type', EmbedType, operator.attrgetter('value'),
        default=EmbedType.RICH
    ),
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
    fields=JsonArray('fields', object=EmbedField)
)


class Embed(JsonObject, template=EmbedTemplate):
    def to_builder(self):
        return EmbedBuilder.from_embed(self)


class EmbedBuilder:
    def __init__(self, **kwargs):
        self.embed = Embed.unmarshal({'fields': []})
        self.set_title(kwargs.get('title'))
        self.set_type(kwargs.get('type'))
        self.set_description(kwargs.get('description'))
        self.set_url(kwargs.get('url'))
        self.set_timestamp(kwargs.get('timestamp'))
        self.set_color(kwargs.get('color'))

    def set_title(self, title):
        if title is not None and not isinstance(title, str):
            raise TypeError(
                f'title should be a string or None, got'
                f'{title.__class__.__name__!r}')

        self.embed.title = title

        return self

    def clear_title(self):
        self.embed.title = None
        return self

    def set_type(self, type):
        self.embed.type = EmbedType(type)
        return self

    def clear_type(self):
        self.embed.type = None
        return self

    def set_description(self, description):
        if description is not None and not isinstance(description, str):
            raise TypeError(
                f'description should be a str or None, got '
                f'{description.__class__.__name__!r}')

        self.embed.description = description

        return self

    def clear_description(self):
        self.embed.description = None
        return self

    def set_url(self, url):
        if url is not None and not isinstance(url, str):
            raise TypeError(
                f'url should be a str or None, got '
                f'{url.__class__.__name__!r}')

        self.embed.url = url

        return self

    def clear_url(self):
        self.embed.url = None
        return self

    def set_timestamp(self, timestamp):
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp)

        if timestamp is not None and not isinstance(timestamp, datetime):
            raise TypeError(
                f'timestamp should be a str, int, float, datetime or None, ',
                f'got {timestamp.__class__.__name__!r}')

        self.embed.timestamp = timestamp

        return self

    def clear_timestamp(self):
        self.embed.timestamp = None
        return self

    def set_color(self, color):
        if color is not None and not isinstance(color, int):
            raise TypeError(
                f'color should be an int, got {color.__class__.__name__!r}')

        self.embed.color = color

        return self

    def clear_color(self):
        self.embed.color = None
        return self

    def set_footer(self, text, icon_url=None, proxy_icon_url=None):
        if not isinstance(text, str):
            raise TypeError(
                f'text should be a str, got {text.__class__.__name__!r}')

        if icon_url is not None and not isinstance(icon_url, str):
            raise TypeError(
                f'icon_url should be a str or None, got '
                f'{icon_url.__class__.__name__!r}')

        if proxy_icon_url is not None and not isinstance(proxy_icon_url, str):
            raise TypeError(
                f'proxy_icon_url should be a str or None, got '
                f'{proxy_icon_url.__class__.__name__!r}')

        self.embed.foooter = EmbedFooter.unmarshal({
            'text': text,
            'icon_url': icon_url,
            'proxy_icon_url': proxy_icon_url
        })

        return self

    def clear_footer(self):
        self.embed.footer = None
        return self

    def _attachment(self, url=None, proxy_url=None, height=None, width=None):
        if url is not None and not isinstance(url, str):
            raise TypeError(
                f'url should be a str or None, got {url.__class__.__name__!r}')

        if proxy_url is not None and not isinstance(proxy_url, str):
            raise TypeError(
                f'proxy_url should be a str or None, got '
                f'{proxy_url.__class__.__name__!r}')

        if height is not None and not isinstance(height, int):
            raise TypeError(
                f'height should be an int or None, got '
                f'{height.__class__.__name__!r}')

        if width is not None and not isinstance(width, int):
            raise TypeError(
                f'width should be an int or None, got '
                f'{width.__class__.__name__!r}')

        return {
            'url': url,
            'proxy_url': proxy_url,
            'height': height,
            'width': width
        }

    def set_image(self, url=None, proxy_url=None, height=None, width=None):
        self.embed.image = EmbedImage.unmarshal(
            self._attachment(url, proxy_url, height, width))
        return self

    def clear_image(self):
        self.embed.image = None

    def set_thumbnail(self, url=None, proxy_url=None, height=None, width=None):
        self.embed.thumbnail = EmbedThumbnail.unmarshal(
            self._attachment(url, proxy_url, height, width))
        return self

    def clear_thumbnail(self):
        self.embed.thumbnail = None
        return self

    def set_video(self, url=None, proxy_url=None, height=None, width=None):
        self.embed.video = EmbedImage.unmarshal(
            self._attachment(url, proxy_url, height, width))
        return self

    def clear_video(self):
        self.embed.video = None
        return self

    def set_provider(self, name=None, url=None):
        if name is not None and not isinstance(name, str):
            raise TypeError(
                f'name should be a str or None, got {name.__class__.__name__}')

        if url is not None and not isinstance(url, str):
            raise TypeError(
                f'url should be a str or None, got {url.__class__.__name__}')

        self.embed.provider = EmbedProvider.unmarshal({
            'name': name,
            'url': url
        })

        return self

    def clear_provider(self):
        self.embed.provider = None
        return self

    def set_author(self, name, icon_url=None, proxy_icon_url=None):
        if not isinstance(name, str):
            raise TypeError(
                f'name should be a str, got {name.__class__.__name__!r}')

        if icon_url is not None and not isinstance(icon_url, str):
            raise TypeError(
                f'icon_url should be a str or None, got '
                f'{icon_url.__class__.__name__!r}')

        if proxy_icon_url is not None and not isinstance(proxy_icon_url, str):
            raise TypeError(
                f'proxy_icon_url should be a str or None, got '
                f'{proxy_icon_url.__class__.__name__!r}')

        self.embed.foooter = EmbedAuthor.unmarshal({
            'name': name,
            'icon_url': icon_url,
            'proxy_icon_url': proxy_icon_url
        })

        return self

    def clear_author(self):
        self.embed.author = None
        return self

    def _field(self, name, value, inline=None):
        if not isinstance(name, str):
            raise TypeError(
                f'name should be a str, got {name.__class__.__name__!r}')

        if not isinstance(value, str):
            raise TypeError(
                f'value should be a str, got {value.__class__.__name__!r}')

        if inline is not None and not isinstance(inline, bool):
            raise TypeError(
                f'inline should be a bool or None, got '
                f'{inline.__class__.__name__!r}')

        return EmbedField.unmarshal({
            'name': name,
            'value': value,
            'inline': inline
        })

    def add_field(self, name, value, inline=None):
        self.embed.fields.append(self._field(name, value, inline))
        return self

    def insert_field(self, index, name, value, inline=None):
        self.embed.fields.insert(index, self._field(name, value, inline))
        return self

    def extend_fields(self, *fields):
        for field in fields:
            self.add_field(*field)
        return self

    def clear_fields(self):
        self.embed.fields.clear()
        return self

    @classmethod
    def from_embed(cls, embed):
        self = cls.__new__(cls)
        self.embed = copy.copy(embed)
        return self
