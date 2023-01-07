from __future__ import annotations

import asyncio
import typing

import wsaio
from loguru import logger

from ..api import GatewayAPI, GatewayOpcode, RawGatewayPayloadTypes
from ..json import load_json

if typing.TYPE_CHECKING:
    from ..clients import WebSocketClient


class Shard:
    def __init__(self, client: WebSocketClient, shard_id: int) -> None:
        self.client = client
        self.shard_id = shard_id

        self.websocket = self.create_websocket()

    @property
    def gateway_api(self) -> GatewayAPI:
        return self.client.gateway_api

    def log(self, level: str, message: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        logger.log(level, '[Shard {}] {}', self.shard_id, message, *args, **kwargs)

    def create_websocket(self) -> GatewayWebSocket:
        return GatewayWebSocket(shard=self)

    async def on_receive(self, payload: RawGatewayPayloadTypes) -> None:
        if payload['op'] == GatewayOpcode.DISPATCH:
            await self.client.dispatch_event(payload['t'], self, payload['d'])

    async def connect(self, gateway_url: str):
        await self.websocket.connect(gateway_url)


class GatewayWebSocket(wsaio.WebSocketClient):
    def __init__(
        self, shard: Shard, *, loop: typing.Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        super().__init__(loop=loop)
        self.shard = shard

    @property
    def api(self) -> GatewayAPI:
        return self.shard.gateway_api

    async def on_text(self, data: str) -> None:
        payload = load_json(data)

        if not isinstance(payload, dict):
            return self.shard.log('warning', 'Gateway sent payload but it was not a JSON object')

        sanitized = self.api.sanitize_payload(payload)
        await self.shard.on_receive(sanitized)

    async def on_binary(self, data: bytes) -> None:
        self.shard.log('warning', 'Gateway closing because a binary payload was received')
        await self.close(data='Binary received.', code=wsaio.WebSocketCloseCode.POLICY_VIOLATION)

    async def on_close(self, data: bytes, code: int) -> None:
        self.shard.log('trace', 'Gateway received close {} (code: {})', data, code)

    async def on_closed(self, exc: typing.Optional[BaseException]) -> None:
        if exc is not None:
            self.shard.log('warning', 'Gateway websocked closed with an exception', exception=exc)
        else:
            self.shard.log('trace', 'Gateway websocket closed')
