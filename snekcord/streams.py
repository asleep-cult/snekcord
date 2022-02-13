from __future__ import annotations

import asyncio
import base64
import collections
import io
import mimetypes
import os
import typing

import aiohttp

if typing.TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    'AsyncReadStream',
    'BufferReadStream',
    'FSReadStream',
    'ResponseReadStream',
)

CHUNK_SIZE = 2 ** 16
DEFAULT_CONTENT_TYPE = 'application/octet-stream'


class AsyncReadStream:
    def __init__(self, *, known_content_type: typing.Optional[str] = None) -> None:
        self.known_content_type = known_content_type
        self.unread: collections.deque[bytes] = collections.deque()

    async def detect_content_type(self) -> str:
        data = await self.aread(4)
        self.unread.append(data)

        if data.startswith((b'\xFF\xD8\xFF\xE0', b'\xFF\xD8\xFF\xE1')):
            return 'image/jpeg'
        elif data.startswith(b'\x89\x50\x4E\x47'):
            return 'image/png'
        elif data.startswith(b'\x47\x49\x46\x38'):
            return 'image/gif'
        elif data.startswith(b'\x7B'):
            return 'application/json'

        return DEFAULT_CONTENT_TYPE

    async def content_type(self) -> str:
        if self.known_content_type is not None:
            return self.known_content_type

        self.known_content_type = await self.detect_content_type()
        return self.known_content_type

    async def extension(self) -> str:
        content_type = await self.content_type()

        extension = mimetypes.guess_extension(content_type)
        if extension is None:
            raise ValueError(f'unknown extension for {content_type!r}')

        return extension

    async def aread(self, amount: int) -> bytes:
        raise NotImplementedError

    async def aiter(self) -> typing.AsyncIterator[bytes]:
        while self.unread:
            yield self.unread.popleft()

        data = await self.aread(CHUNK_SIZE)
        while data:
            yield data
            data = await self.aread(CHUNK_SIZE)

    async def aread_all(self) -> bytes:
        buffer = io.BytesIO()

        async for chunk in self.aiter():
            buffer.write(chunk)

        return buffer.getvalue()

    async def to_data_uri(self) -> str:
        content_type = await self.content_type()
        data = await self.aread_all()

        return f'data:{content_type};base64,{base64.b64encode(data)}'


class BufferReadStream(AsyncReadStream):
    def __init__(self, buffer: io.BytesIO, known_content_type: typing.Optional[str] = None) -> None:
        self.buffer = buffer
        super().__init__(known_content_type=known_content_type)

    @classmethod
    def from_bytes(cls, data: bytes, known_content_type: typing.Optional[str] = None) -> Self:
        self = cls.__new__(cls)
        self.buffer = io.BytesIO(data)

        AsyncReadStream.__init__(self, known_content_type=known_content_type)
        return self

    async def aread(self, amount: int) -> bytes:
        return self.buffer.read(amount)


class FSReadStream(AsyncReadStream):
    def __init__(
        self, path: os.PathLike[str], *, known_content_type: typing.Optional[str] = None
    ) -> None:
        self.path = path
        self.fp: typing.Optional[typing.IO[bytes]] = None

        if known_content_type is None:
            known_content_type = mimetypes.guess_type(self.path)[0]

        super().__init__(known_content_type=known_content_type)

    @classmethod
    def from_fp(cls, fp: typing.IO[bytes], known_content_type: typing.Optional[str] = None) -> Self:
        self = cls.__new__(cls)
        self.path = None
        self.fp = fp

        AsyncReadStream.__init__(self, known_content_type=known_content_type)
        return self

    def read(self, amount: int) -> bytes:
        if self.fp is None:
            self.fp = open(self.path, 'rb')

        return self.fp.read(amount)

    async def aread(self, amount: int) -> bytes:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.read, amount)


class ResponseReadStream(AsyncReadStream):
    def __init__(
        self, response: aiohttp.ClientResponse, *, known_content_type: typing.Optional[str] = None
    ) -> None:
        self.response = response

        if known_content_type is None:
            known_content_type = response.content_type

        super().__init__(known_content_type=known_content_type)

    async def aread(self, amount: int) -> bytes:
        return await self.response.content.read(amount)
