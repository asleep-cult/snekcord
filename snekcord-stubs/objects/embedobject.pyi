from __future__ import annotations

import typing as t
from datetime import datetime

from .channelobject import TextChannel
from .messageobject import Message
from ..utils.enum import Enum
from ..utils.json import JsonObject, JsonTemplate


class EmbedType(Enum[str]):
    RICH = 'rich'
    IMAGE = 'image'
    VIDEO = 'video'
    GIFV = 'gifv'
    ARTICLE = 'article'
    LINK = 'link'


EmbedThumbnailTemplate: JsonTemplate = ...


class EmbedThumbnail(JsonObject, template=EmbedThumbnailTemplate):
    user: str
    proxy_url: str
    height: int
    width: int


EmbedVideoTemplate: JsonTemplate = ...


class EmbedVideo(JsonObject, template=EmbedVideoTemplate):
    url: str
    proxy_url: str
    height: int
    width: int


EmbedImageTemplate: JsonTemplate = ...


class EmbedImage(JsonObject, template=EmbedImageTemplate):
    url: str
    proxy_url: str
    height: int
    width: int


EmbedProviderTemplate: JsonTemplate = ...


class EmbedProvider(JsonObject, template=EmbedProviderTemplate):
    name: str
    url: str


EmbedAuthorTemplate: JsonTemplate = ...


class EmbedAuthor(JsonObject, template=EmbedAuthorTemplate):
    name: str
    icon_url: str
    proxy_icon_url: str


EmbedFooterTemplate: JsonTemplate = ...


class EmbedFooter(JsonObject, template=EmbedFooterTemplate):
    text: str
    icon_url: str
    proxy_icon_url: str


EmbedFieldTemplate: JsonTemplate = ...


class EmbedField(JsonObject, template=EmbedFieldTemplate):
    name: str
    value: str
    inline: bool


EmbedTemplate: JsonTemplate = ...


class Embed(JsonObject, template=EmbedTemplate):
    title: str
    type: EmbedType
    description: str
    url: str
    timestamp: datetime
    color: int
    footer: EmbedFooter
    image: EmbedImage
    thumbnail: EmbedThumbnail
    video: EmbedVideo
    provider: EmbedProvider
    author: EmbedAuthor
    fields: EmbedField


class EmbedBuilder:
    embed: Embed

    def __init__(self, title: str | None = ..., type: str | None = ...,
                 description: str | None = ..., url: str | None = ...,
                 timestamp: str | float | datetime | None = ...,
                 color: int | None = ...) -> None: ...

    @classmethod
    def from_embed(cls, embed: Embed) -> EmbedBuilder: ...

    def set_title(self, title: str | None) -> EmbedBuilder: ...

    def clear_title(self) -> EmbedBuilder: ...

    def set_type(self, type: str | None) -> EmbedBuilder: ...

    def clear_type(self) -> EmbedBuilder: ...

    def set_description(self, description: str | None) -> EmbedBuilder: ...

    def clear_description(self) -> EmbedBuilder: ...

    def set_url(self, url: str | None) -> EmbedBuilder: ...

    def clear_url(self) -> EmbedBuilder: ...

    def set_timestamp(self, timestamp: str | float | datetime | None
                      ) -> EmbedBuilder: ...

    def clear_timestamp(self) -> EmbedBuilder: ...

    def set_color(self, color: int | None) -> EmbedBuilder: ...

    def set_footer(self, text: str, icon_url: str | None = ...,
                   proxy_icon_url: str | None = ...) -> EmbedBuilder: ...

    def clear_footer(self) -> EmbedBuilder: ...

    def set_image(self, url: str | None = ...,
                  proxy_url: str | None = ...,
                  height: int | None = ...,
                  width: int | None = ...) -> EmbedBuilder: ...

    def clear_image(self) -> EmbedBuilder: ...

    def set_thumbnail(self, url: str | None = ...,
                      proxy_url: str | None = ...,
                      height: int | None = ...,
                      width: int | None = ...) -> EmbedBuilder: ...

    def clear_thumbnail(self) -> EmbedBuilder: ...

    def set_video(self, url: str | None = ...,
                  proxy_url: str | None = ...,
                  height: int | None = ...,
                  width: int | None = ...) -> EmbedBuilder: ...

    def clear_video(self) -> EmbedBuilder: ...

    def set_provider(self, name: str | None = ...,
                     url: str | None = ...) -> EmbedBuilder: ...

    def clear_provider(self) -> EmbedBuilder: ...

    def set_author(self, name: str, icon_url: str | None = ...,
                   proxy_icon_url: str | None = ...) -> EmbedBuilder: ...

    def add_field(self, name: str, value: str,
                  inline: bool | None = ...) -> EmbedBuilder: ...

    def insert_field(self, index: int, name: str, value: str,
                     inline: bool | None = ...) -> EmbedBuilder: ...

    def extend_fields(self, *fields: tuple[str, str] | tuple[str, str, bool]
                      ) -> EmbedBuilder: ...

    def clear_fields(self) -> EmbedBuilder: ...

    def send_to(self, channel: TextChannel,
                **kwargs: t.Any) -> Message: ...
