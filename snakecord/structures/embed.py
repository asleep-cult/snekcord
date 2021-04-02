from ..utils import JsonArray, JsonField, JsonStructure


class EmbedAttachment(JsonStructure, base=False):
    __json_fields__ = {
        'url': JsonField('url'),
        'proxy_url': JsonField('proxy_url'),
        'height': JsonField('height'),
        'width': JsonField('width'),
    }


class EmbedVideo(JsonStructure, base=False):
    __json_fields__ = {
        'url': JsonField('url'),
        'height': JsonField('height'),
        'width': JsonField('width'),
    }


class EmbedProvider(JsonStructure, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
        'url': JsonField('url'),
    }


class EmbedAuthor(JsonStructure, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
        'url': JsonField('url'),
        'icon_url': JsonField('icon_url'),
        'proxy_icon_url': JsonField('proxy_icon_url'),
    }


class EmbedFooter(JsonStructure, base=False):
    __json_fields__ = {
        'text': JsonField('text'),
        'icon_url': JsonField('icon_url'),
        'proxy_icon_url': JsonField('proxy_icon_url'),
    }


class EmbedField(JsonStructure, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
        'value': JsonField('value'),
        'inline': JsonField('inline'),
    }


class Embed(JsonStructure, base=False):
    __json_fields__ = {
        'title': JsonField('title'),
        'type': JsonField('type'),
        'description': JsonField('description'),
        'url': JsonField('url'),
        'color': JsonField('color'),
        'footer': JsonField('footer', struct=EmbedFooter),
        'image': JsonField('image', struct=EmbedAttachment),
        'thumbnail': JsonField('thumbnail', struct=EmbedAttachment),
        'video': JsonField('video', struct=EmbedVideo),
        'provider': JsonField('provider', struct=EmbedProvider),
        'author': JsonField('author', struct=EmbedAuthor),
        'fields': JsonArray('fields', struct=EmbedField),
    }
