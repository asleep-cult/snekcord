from __future__ import annotations

import typing as t
from datetime import datetime

from .channelobject import TextChannel
from .messageobject import Message
from ..utils.enum import Enum
from ..utils.json import JsonArray, JsonField, JsonObject


class EmbedType(Enum[str]):
    RICH: str
    IMAGE: str
    VIDEO: str
    GIFV: str
    ARTICLE: str
    LINK: str


class EmbedThumbnail(JsonObject):
    user: t.ClassVar[JsonField[str]]
    proxy_url: t.ClassVar[JsonField[str]]
    height: t.ClassVar[JsonField[int]]
    width: t.ClassVar[JsonField[int]]


class EmbedVideo(JsonObject):
    url: t.ClassVar[JsonField[str]]
    proxy_url: t.ClassVar[JsonField[str]]
    height: t.ClassVar[JsonField[int]]
    width: t.ClassVar[JsonField[int]]


class EmbedImage(JsonObject):
    url: t.ClassVar[JsonField[str]]
    proxy_url: t.ClassVar[JsonField[str]]
    height: t.ClassVar[JsonField[int]]
    width: t.ClassVar[JsonField[int]]


class EmbedProvider(JsonObject):
    name: t.ClassVar[JsonField[str]]
    url: t.ClassVar[JsonField[str]]


class EmbedAuthor(JsonObject):
    name: t.ClassVar[JsonField[str]]
    icon_url: t.ClassVar[JsonField[str]]
    proxy_icon_url: t.ClassVar[JsonField[str]]


class EmbedFooter(JsonObject):
    text: t.ClassVar[JsonField[str]]
    icon_url: t.ClassVar[JsonField[str]]
    proxy_icon_url: t.ClassVar[JsonField[str]]


class EmbedField(JsonObject):
    name: t.ClassVar[JsonField[str]]
    value: t.ClassVar[JsonField[str]]
    inline: t.ClassVar[JsonField[bool]]


class Embed(JsonObject):
    title: t.ClassVar[JsonField[str]]
    type: t.ClassVar[JsonField[EmbedType]]
    description: t.ClassVar[JsonField[str]]
    url: t.ClassVar[JsonField[str]]
    timestamp: t.ClassVar[JsonField[datetime]]
    color: t.ClassVar[JsonField[int]]
    footer: t.ClassVar[JsonField[EmbedFooter]]
    image: t.ClassVar[JsonField[EmbedImage]]
    thumbnail: t.ClassVar[JsonField[EmbedThumbnail]]
    video: t.ClassVar[JsonField[EmbedVideo]]
    provider: t.ClassVar[JsonField[EmbedProvider]]
    author: t.ClassVar[JsonField[EmbedAuthor]]
    fields: t.ClassVar[JsonArray[EmbedField]]


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

    def send_to(self, channel: TextChannel, **kwargs: t.Any) -> Message: ...
