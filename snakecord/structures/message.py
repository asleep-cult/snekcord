from .base import BaseObject
from .embed import Embed
from ..utils import JsonArray, JsonField, JsonStructure, Snowflake


class MessageActivity(JsonStructure):
    __json_fields__ = {
        'type': JsonField('type'),
        'party_id': JsonField('party_id'),
    }


class MessageApplication(BaseObject):
    __json_fields__ = {
        'cover_image': JsonField('cover_image'),
        'description': JsonField('description'),
        'icon': JsonField('icon'),
        'name': JsonField('name'),
    }


class MessageReference(JsonStructure):
    __json_fields__ = {
        'message_id': JsonField('message_id', Snowflake, str),
        'channel_id': JsonField('channel_id', Snowflake, str),
        'guild_id': JsonField('guild_id', int, str),
    }


class MessageSticker(BaseObject):
    __json_fields__ = {
        'pack_id': JsonField('pack_id', Snowflake, str),
        'name': JsonField('name'),
        'description': JsonField('description'),
        'tags': JsonField('tags'),
        'asset': JsonField('asset'),
        'preview_asset': JsonField('preview_asset'),
        'format_type': JsonField('format_type'),
    }


class FollowedChannel(JsonStructure):
    __json_fields__ = {
        'channel_id': JsonField('channel_id', Snowflake, str),
        'webhook_id': JsonField('webhook_id', Snowflake, str),
    }


class MessageAttachment(BaseObject):
    __json_fields__ = {
        'filename': JsonField('filename'),
        'size': JsonField('size'),
        'url': JsonField('url'),
        'proxy_url': JsonField('proxy_url'),
        'height': JsonField('height'),
        'width': JsonField('width'),
    }


class Message(BaseObject):
    __json_fields__ = {
        'channel_id': JsonField('channel_id', Snowflake, str),
        'guild_id': JsonField('guild_id', Snowflake, str),
        '_author': JsonField('author'),
        '_member': JsonField('member'),
        'content': JsonField('content'),
        'tts': JsonField('tts'),
        'mention_everyone': JsonField('mention_everyone'),
        'attachments': JsonArray('attachments', struct=MessageAttachment),
        'embeds': JsonArray('embeds', struct=Embed, init_struct_class=False),
        '_reactions': JsonArray('reactions'),
        'nonce': JsonField('nonce'),
        'pinned': JsonField('pinned'),
        'webhook_id': JsonField('webhook_id', int, str),
        'type': JsonField('type'),
        'activity': JsonField('activity', struct=MessageActivity),
        'application': JsonField('application'),
        'flags': JsonField('flags'),
        'stickers': JsonArray('stickers', struct=MessageSticker),
    }
