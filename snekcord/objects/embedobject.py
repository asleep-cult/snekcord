import copy
import enum
import operator
from datetime import datetime

from ..utils import JsonArray, JsonField, JsonObject, JsonTemplate

__all__ = ('EmbedType', 'EmbedThumbnail', 'EmbedVideo', 'EmbedImage',
           'EmbedProvider', 'EmbedAuthor', 'EmbedFooter', 'EmbedField',
           'Embed', 'EmbedBuilder')


class EmbedType(enum.Enum):
    """An enumeration of Discord's embed types

    | Name      | Description                                        |
    | --------- | -------------------------------------------------- |
    | `RICH`    | Generic embed rendered from attributes             |
    | `IMAGE`   | Image embed                                        |
    | `VIDEO`   | Video embed                                        |
    | `GIFV`    | Animated gif image embed rendered as a video embed |
    | `ARTICLE` | Article embed                                      |
    | `LINK`    | Link embed                                         |

    warning:
        This is not used by Discord and should be considered deprecated
    """
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
"""An embed thumbnail

Attributes:
    url str: The thumbnail's url

    proxy_url str: The thumbnail's proxy url

    height int: The thumbnail's height

    width int: The thumbnail's width
"""


EmbedVideo = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width')
).default_object('EmbedVideo')
"""An embed video

Attributes:
    url str: The video's url

    proxy_url str: The video's proxy url

    height int: The video's height

    width int: The video's width
"""


EmbedImage = JsonTemplate(
    url=JsonField('url'),
    proxy_url=JsonField('proxy_url'),
    height=JsonField('height'),
    width=JsonField('width')
).default_object('EmbedImage')
"""An embed image

Attributes:
    url str: The image's url

    proxy_url str: The image's proxy url

    height int: The image's height

    width int: The image's width
"""


EmbedProvider = JsonTemplate(
    name=JsonField('name'),
    url=JsonField('url')
).default_object('EmbedProvider')
"""An embed provider

Attributes:
    name str: The provider's name

    url str: The provider's url
"""


EmbedAuthor = JsonTemplate(
    name=JsonField('name'),
    icon_url=JsonField('icon_url'),
    proxy_icon_url=JsonField('proxy_icon_url')
).default_object('EmbedAuthor')
"""An embed author

Attributes:
    name str: The author's name

    icon_url str: The author's icon url

    proxy_icon_url str: The author's proxy icon url
"""


EmbedFooter = JsonTemplate(
    text=JsonField('text'),
    icon_url=JsonField('icon_url'),
    proxy_icon_url=JsonField('proxy_icon_url')
).default_object('EmbedFooter')
"""An embed footer

Attributes:
    text str: The footer's text

    icon_url str: The footer's icon url

    proxy_icon_url str: The footer's proxy icon url
"""


EmbedField = JsonTemplate(
    name=JsonField('name'),
    value=JsonField('value'),
    inline=JsonField('inline')
).default_object('EmbedField')
"""An embed field

Attributes:
    name str: The field's name

    value str: The field's value

    inline bool: Whether or not the field is inline
"""


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
    """Represents embedded rich content in a `Message`

    Attributes:
        title str: The embed's title

        type EmbedType: The embed's type

        description str: The embed's description

        url str: The embed's url

        timestamp datetime: The embed's timestamp

        color int: The embed's color

        footer EmbedFooter: The embed's footer

        image EmbedImage: The embed's image

        thumbnail EmbedThumbnail: The embed's thumbnail

        video EmbedVideo: The embed's video

        provider EmbedProvider: The embed's provider

        author EmbedAuthor: The embed's author

        fields list[EmbedField]: The embed's fields
    """
    def to_builder(self):
        """Equivalent to `EmbedBuilder.from_embed(self)`"""
        return EmbedBuilder.from_embed(self)


class EmbedBuilder:
    """A class that helps with building `Embed`s

    Attributes:
        embed Embed: The underlying embed object

    note:
        All methods in this class return the builder
    """
    def __init__(self, **kwargs):
        """
        Accepts `title`, `type`, `description`, `url`, `timestamp` and `color`
        keyword arguments, see the corresponding `set_*` methods for more
        information
        """
        self.embed = Embed.unmarshal({'fields': []})
        self.set_title(kwargs.get('title'))
        self.set_type(kwargs.get('type'))
        self.set_description(kwargs.get('description'))
        self.set_url(kwargs.get('url'))
        self.set_timestamp(kwargs.get('timestamp'))
        self.set_color(kwargs.get('color'))

    def set_title(self, title):
        """Sets the embed's title

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        if title is not None and not isinstance(title, str):
            raise TypeError(
                f'title should be a str or None, got'
                f'{title.__class__.__name__!r}')

        self.embed.title = title

        return self

    def clear_title(self):
        """Clears the embed's title"""
        self.embed.title = None
        return self

    def set_type(self, type):
        """Sets the embed's type

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        self.embed.type = EmbedType(type) if type is not None else None
        return self

    def clear_type(self):
        """Clears embed's type"""
        self.embed.type = None
        return self

    def set_description(self, description):
        """Sets the embed's description

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        if description is not None and not isinstance(description, str):
            raise TypeError(
                f'description should be a str or None, got '
                f'{description.__class__.__name__!r}')

        self.embed.description = description

        return self

    def clear_description(self):
        """Clears the embed's description"""
        self.embed.description = None
        return self

    def set_url(self, url):
        """Sets the embed's url

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        if url is not None and not isinstance(url, str):
            raise TypeError(
                f'url should be a str or None, got '
                f'{url.__class__.__name__!r}')

        self.embed.url = url

        return self

    def clear_url(self):
        """Clears the embed's url"""
        self.embed.url = None
        return self

    def set_timestamp(self, timestamp):
        """Sets the embed's timestamp

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
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
        """Clears the embed's timestamp"""
        self.embed.timestamp = None
        return self

    def set_color(self, color):
        """Sets the embed's color

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        if color is not None and not isinstance(color, int):
            raise TypeError(
                f'color should be an int, got {color.__class__.__name__!r}')

        self.embed.color = color

        return self

    def clear_color(self):
        """Clears the embed's color"""
        self.embed.color = None
        return self

    def set_footer(self, text, icon_url=None, proxy_icon_url=None):
        """Sets the embed's footer

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
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

        self.embed.footer = EmbedFooter.unmarshal({
            'text': text,
            'icon_url': icon_url,
            'proxy_icon_url': proxy_icon_url
        })

        return self

    def clear_footer(self):
        """Clears the embed's footer"""
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
        """Sets the embed's image

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        self.embed.image = EmbedImage.unmarshal(
            self._attachment(url, proxy_url, height, width))
        return self

    def clear_image(self):
        """Clears the embed's image"""
        self.embed.image = None

    def set_thumbnail(self, url=None, proxy_url=None, height=None, width=None):
        """Sets the embed's thumbnail

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        self.embed.thumbnail = EmbedThumbnail.unmarshal(
            self._attachment(url, proxy_url, height, width))
        return self

    def clear_thumbnail(self):
        """Clears the embed's thumbnail"""
        self.embed.thumbnail = None
        return self

    def set_video(self, url=None, proxy_url=None, height=None, width=None):
        """Sets the embed's video

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        self.embed.video = EmbedImage.unmarshal(
            self._attachment(url, proxy_url, height, width))
        return self

    def clear_video(self):
        """Clears the embed's video"""
        self.embed.video = None
        return self

    def set_provider(self, name=None, url=None):
        """Sets the embed's provider

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
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
        """Clears the embed's provider"""
        self.embed.provider = None
        return self

    def set_author(self, name, icon_url=None, proxy_icon_url=None):
        """Sets the embed's author

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
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

        self.embed.author = EmbedAuthor.unmarshal({
            'name': name,
            'icon_url': icon_url,
            'proxy_icon_url': proxy_icon_url
        })

        return self

    def clear_author(self):
        """Clears the embed's author"""
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
        """Adds a field to the embed

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        self.embed.fields.append(self._field(name, value, inline))
        return self

    def insert_field(self, index, name, value, inline=None):
        """Inserts a field into the embed at `index`

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        self.embed.fields.insert(index, self._field(name, value, inline))
        return self

    def extend_fields(self, *fields):
        """Adds multiple fields of `(name, value, inline=None)` to the embed

        Examples:
            ```py
            builder = snekcord.EmbedBuilder()
            builder.add_fields(
                ('Hello', 'World'),
                ('Goodbye', 'World', False),
            )
            ```

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        for field in fields:
            self.add_field(*field)
        return self

    def clear_fields(self):
        """Clears the fields of the embed"""
        self.embed.fields.clear()
        return self

    async def send_to(self, channel, **kwargs):
        """Sends the embed to `channel` with `**kwargs`, equivalent to
        `await channel.messages.create(embed=self.embed)`
        """
        kwargs['embed'] = self.embed
        return await channel.messages.create(**kwargs)

    @classmethod
    def from_embed(cls, embed):
        """Creates a builder from an `Embed`

        Arguments:
            embed Embed: The embed to create a builder from

        Returns:
            EmbedBuilder: The builder
        """
        self = cls.__new__(cls)
        self.embed = copy.copy(embed)
        return self
