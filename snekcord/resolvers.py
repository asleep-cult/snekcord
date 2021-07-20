import base64
import io
import re

from .fetchables import Fetchable
from .objects.embedobject import Embed, EmbedBuilder
from .utils import Snowflake

CHANNEL_MENTION_RE = re.compile(r'<#(?P<id>\d{17,19})>')
EMOJI_RE = re.compile(r'<(?P<animated>a)?:(?P<name>[\w\d_]{2,32}):(?P<id>\d{17,19})>')
ROLE_MENTION_RE = re.compile(r'<@&(?P<id>\d{17,19})>')
USER_MENTION_RE = re.compile(r'<@!?(?P<id>\d{17,19})>')

IMAGE_DATA_FORMATS = ('data:image/jpeg;base64,', 'data:image/png;base64,', 'data:image/gif;base64,')


async def resolve_image_data(image):
    # https://gist.github.com/leommoore/f9e57ba2aa4bf197ebc5

    if isinstance(image, Fetchable):
        image = await image.fetch()

    if isinstance(image, str):
        try:
            image = open(image, 'rb')
        except FileNotFoundError:
            pass

    if isinstance(image, io.IOBase):
        if image.seekable():
            image.seek(0)
        else:
            assert image.tell() == 0

        image = image.read()

    if isinstance(image, bytes):
        if image.startswith((b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xE1')):
            data = base64.b64encode(image).decode('ascii')
            return f'data:image/jpeg;base64,{data}'

        elif image.startswith(b'\x89\x50\x4E\x47'):
            data = base64.b64encode(image).decode('ascii')
            return f'data:image/png;base64,{data}'

        elif image.startswith(b'\x47\x49\x46\x38'):
            data = base64.b64encode(image).decode('ascii')
            return f'data:image/gif;base64,{data}'

        image = image.decode('ascii')

    if isinstance(image, str):
        if image.startswith(IMAGE_DATA_FORMATS):
            return image

    raise TypeError('Failed to resolve image data')


def resolve_embed_data(embed):
    if isinstance(embed, EmbedBuilder):
        embed = embed.embed

    if isinstance(embed, Embed):
        return embed.to_dict()

    raise TypeError('Failed to resolve embed data')


def resolve_channel_mentions(string):
    for match in CHANNEL_MENTION_RE.finditer(string):
        yield Snowflake(match.group('id'))


def resolve_channel_mention(string):
    match = CHANNEL_MENTION_RE.match(string)
    if match is not None:
        return Snowflake(match.group('id'))
    return None


def resolve_emojis(string):
    for match in EMOJI_RE.finditer(string):
        yield {
            'animated': bool(match.group('animated')),
            'name': match.group('name'),
            'id': Snowflake(match.group('id')),
        }


def resolve_emoji(string):
    match = EMOJI_RE.match(string)
    if match is not None:
        return {
            'animated': bool(match.group('animated')),
            'name': match.group('name'),
            'id': Snowflake(match.group('id')),
        }
    return None


def resolve_role_mentions(string):
    for match in ROLE_MENTION_RE.finditer(string):
        yield Snowflake(match.group('id'))


def resolve_role_mention(string):
    match = ROLE_MENTION_RE.match(string)
    if match is not None:
        return Snowflake(match.group('id'))
    return None


def resolve_user_mentions(string):
    for match in USER_MENTION_RE.finditer(string):
        yield Snowflake(match.group('id'))


def resolve_user_mention(string):
    match = USER_MENTION_RE.match(string)
    if match is not None:
        return Snowflake(match.group('id'))
    return None
