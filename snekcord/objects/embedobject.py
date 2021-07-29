import copy
from datetime import datetime

from ..enums import EmbedType
from ..json import JsonArray, JsonField, JsonObject

__all__ = (
    'EmbedThumbnail', 'EmbedVideo', 'EmbedImage', 'EmbedProvider', 'EmbedAuthor',
    'EmbedFooter', 'EmbedField', 'Embed', 'EmbedBuilder'
)


class EmbedThumbnail(JsonObject):
    """An embed thumbnail

    Attributes:
        url str: The thumbnail's url

        proxy_url str: The thumbnail's proxy url

        height int: The thumbnail's height

        width int: The thumbnail's width
    """
    url = JsonField('url')
    proxy_url = JsonField('proxy_url')
    height = JsonField('height')
    width = JsonField('width')


class EmbedVideo(JsonObject):
    """An embed video

    Attributes:
        url str: The video's url

        proxy_url str: The video's proxy url

        height int: The video's height

        width int: The video's width
    """
    url = JsonField('url')
    proxy_url = JsonField('proxy_url')
    height = JsonField('height')
    width = JsonField('width')


class EmbedImage(JsonObject):
    """An embed image

    Attributes:
        url str: The image's url

        proxy_url str: The image's proxy url

        height int: The image's height

        width int: The image's width
    """
    url = JsonField('url')
    proxy_url = JsonField('proxy_url')
    height = JsonField('height')
    width = JsonField('width')


class EmbedProvider(JsonObject):
    """An embed provider

    Attributes:
        name str: The provider's name

        url str: The provider's url
    """
    name = JsonField('name')
    url = JsonField('url')


class EmbedAuthor(JsonObject):
    """An embed author

    Attributes:
        name str: The author's name

        icon_url str: The author's icon url

        proxy_icon_url str: The author's proxy icon url
    """
    name = JsonField('name')
    icon_url = JsonField('icon_url')
    proxy_icon_url = JsonField('proxy_icon_url')


class EmbedFooter(JsonObject):
    """An embed footer

    Attributes:
        text str: The footer's text

        icon_url str: The footer's icon url

        proxy_icon_url str: The footer's proxy icon url
    """
    text = JsonField('text')
    icon_url = JsonField('icon_url')
    proxy_icon_url = JsonField('proxy_icon_url')


class EmbedField(JsonObject):
    """An embed field

    Attributes:
        name str: The field's name

        value str: The field's value

        inline bool: Whether or not the field is inline
    """
    name = JsonField('name')
    value = JsonField('value')
    inline = JsonField('inline')


class Embed(JsonObject):
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
    title = JsonField('title'),
    type = JsonField('type', EmbedType.get_enum, default=EmbedType.RICH)
    description = JsonField('description')
    url = JsonField('url')
    timestamp = JsonField('timestamp', datetime.fromisoformat)
    color = JsonField('color')
    footer = JsonField('footer', object=EmbedFooter)
    image = JsonField('image', object=EmbedImage)
    thumbnail = JsonField('thumbnail', object=EmbedThumbnail)
    video = JsonField('video', object=EmbedVideo)
    provider = JsonField('provider', object=EmbedProvider)
    author = JsonField('author', object=EmbedAuthor)
    fields = JsonArray('fields', object=EmbedField)

    def to_builder(self):
        """Equivalent to `EmbedBuilder.from_embed(self)`"""
        return EmbedBuilder.from_embed(self)


class EmbedBuilder:
    """A class that helps with building `Embed`s

    Attributes:
        embed Embed: The underlying embed object

    note:
        All methods in this class return the builder except for `send_to`
    """
    def __init__(
        self, title=None, type=None, description=None, url=None, timestamp=None, color=None
    ):
        """
        Accepts `title`, `type`, `description`, `url`, `timestamp` and `color`
        keyword arguments, see the corresponding `set_*` methods for more
        information
        """
        self.embed = Embed.unmarshal({'fields': []})

        if title is not None:
            self.set_title(title)

        if type is not None:
            self.set_type(type)

        if description is not None:
            self.set_description(description)

        if url is not None:
            self.set_url(url)

        if timestamp is not None:
            self.set_timestamp(timestamp)

        if color is not None:
            self.set_color(color)

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

    def set_title(self, title):
        """Sets the embed's title"""
        self.embed._json_data_['title'] = str(title)
        return self

    def clear_title(self):
        """Clears the embed's title"""
        self.embed._json_data_.pop('type', None)
        return self

    def set_type(self, type):
        """Sets the embed's type"""
        if type is not None:
            type = EmbedType.get_enum(type)

        self.embed._json_data_['type'] = type

        return self

    def clear_type(self):
        """Clears embed's type"""
        self.embed._json_fields_.pop('type', None)
        return self

    def set_description(self, description):
        """Sets the embed's description"""
        self.embed._json_data_['description'] = str(description)
        return self

    def clear_description(self):
        """Clears the embed's description"""
        self.embed._json_fields_.pop('description', None)
        return self

    def set_url(self, url):
        """Sets the embed's url"""
        self.embed._json_data_['url'] = str(url)
        return self

    def clear_url(self):
        """Clears the embed's url"""
        self.embed._json_fields_.pop('url', None)
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
                f'got {timestamp.__class__.__name__!r}'
            )

        self.embed._json_data_['timestamp'] = timestamp.isoformat()

        return self

    def clear_timestamp(self):
        """Clears the embed's timestamp"""
        self.embed._json_fields_.pop('timestamp', None)
        return self

    def set_color(self, color):
        """Sets the embed's color"""
        self.embed._json_data_['color'] = int(color)
        return self

    def clear_color(self):
        """Clears the embed's color"""
        self.embed._json_data_.pop('color', None)
        return self

    def set_footer(self, text, *, icon_url=None, proxy_icon_url=None):
        """Sets the embed's footer"""
        json = {'text': str(text)}

        if icon_url is not None:
            json['icon_url'] = str(icon_url)

        if proxy_icon_url is not None:
            json['proxy_icon_url'] = str(proxy_icon_url)

        self.embed.update({'footer': json})

        return self

    def clear_footer(self):
        """Clears the embed's footer"""
        self.embed._json_data_['footer'] = None
        return self

    def _attachment(self, url, proxy_url, height, width):
        json = {}

        if url is not None:
            json['url'] = str(url)

        if proxy_url is not None:
            json['proxy_url'] = str(proxy_url)

        if height is not None:
            json['height'] = int(height)

        if width is not None:
            json['width'] = int(width)

        return json

    def set_image(self, *, url=None, proxy_url=None, height=None, width=None):
        """Sets the embed's image"""
        self.embed.update({'image': self._attachment(url, proxy_url, height, width)})
        return self

    def clear_image(self):
        """Clears the embed's image"""
        self.embed._json_data_.pop('image', None)
        return self

    def set_thumbnail(self, *, url=None, proxy_url=None, height=None, width=None):
        """Sets the embed's thumbnail"""
        self.embed.update({'thumbnail': self._attachment(url, proxy_url, height, width)})
        return self

    def clear_thumbnail(self):
        """Clears the embed's thumbnail"""
        self.embed._json_data_.pop('thumbnail', None)
        return self

    def set_video(self, *, url=None, proxy_url=None, height=None, width=None):
        """Sets the embed's video"""
        self.embed.update({'video': self._attachment(url, proxy_url, height, width)})
        return self

    def clear_video(self):
        """Clears the embed's video"""
        self.embed._json_data_.pop('video', None)
        return self

    def set_provider(self, *, name=None, url=None):
        """Sets the embed's provider"""
        json = {}

        if name is not None:
            json['name'] = str(name)

        if url is not None:
            json['url'] = str(url)

        self.embed.update({'provider': json})

        return self

    def clear_provider(self):
        """Clears the embed's provider"""
        self.embed._json_data_['provider'] = None
        return self

    def set_author(self, name, *, icon_url=None, proxy_icon_url=None):
        """Sets the embed's author

        Raises:
            TypeError: Raised when an invalid argument type is provided
        """
        json = {'name': str(name)}

        if icon_url is not None:
            json['icon_url'] = str(icon_url)

        if proxy_icon_url is not None:
            json['proxy_icon_url'] = proxy_icon_url

        self.embed.update({'author': json})

        return self

    def clear_author(self):
        """Clears the embed's author"""
        self.embed._json_data_.pop('author', None)
        return self

    def _field(self, name, value, inline):
        json = {'name': str(name), 'value': str(value)}

        if inline is not None:
            json['inline'] = bool(inline)

        return json

    def add_field(self, name, value, *, inline=None):
        """Adds a field to the embed"""
        self.embed._json_data_['fields'].append(self._field(name, value, inline))
        return self

    def add_fields(self, *fields):
        """Adds multiple fields of to the embed"""
        for field in fields:
            self.add_field(*field)
        return self

    def insert_field(self, index, name, value, *, inline=None):
        """Inserts a field into the embed at `index`"""
        self.embed._json_data_['fields'].insert(index, self._field(name, value, inline))
        return self

    def clear_fields(self):
        """Clears the fields of the embed"""
        self.embed._json_data_['fields'].clear()
        return self

    def send_to(self, destination, **kwargs):
        """Sends the embed to `destination` with `**kwargs`, equivalent to
        `await destination.messages.create(embed=self.embed)`
        """
        kwargs['embed'] = self.embed
        return destination.messages.create(**kwargs)
