from __future__ import annotations

from typing import TYPE_CHECKING

from .base_state import BaseCachedState
from ..events import (
    BaseEvent,
    GuildAvailableEvent,
    GuildDeleteEvent,
    GuildEvent,
    GuildJoinEvent,
    GuildReceiveEvent,
    GuildUpdateEvent,
)
from ..intents import WebSocketIntents
from ..objects import (
    Guild,
    ObjectWrapper,
)
from ..rest.endpoints import (
    GET_GUILD,
)
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import ShardWebSocket

__all__ = ('GuildState',)


class GuildState(BaseCachedState):
    @classmethod
    def unwrap_id(cls, object):
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (int, str)):
            return Snowflake(object)

        if isinstance(object, Guild):
            return object.id

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, cls):
                return object

            raise TypeError('Expected ObjectWrapper created by GuildState')

        raise TypeError('Expected Snowflake, int, str, Guild or ObjectWrapper')

    async def upsert(self, data):
        guild = self.get(data['id'])
        if guild is not None:
            guild.update(data)
        else:
            guild = Guild.unmarshal(data, state=self)

        owner_id = data.get('owner_id')
        if owner_id is not None:
            guild.owner.set_id(owner_id)

        if 'widget_channel_id' in data:
            guild.widget_channel.set_id(data['widget_channel_id'])

        if 'system_channel_id' in data:
            guild.system_channel.set_id(data['system_channel_id'])

        if 'rules_channel_id' in data:
            guild.rules_channel.set_id(data['rules_channel_id'])

        roles = data.get('roles')
        if roles is not None:
            await guild._update_roles(roles)

        members = data.get('members')
        if members is not None:
            # await guild._update_members(members)
            pass

        emojis = data.get('emojis')
        if emojis is not None:
            await guild._update_emojis(emojis)

        channels = data.get('channels')
        if channels is not None:
            await guild._update_channels(channels)

        return guild

    async def fetch(self, guild):
        guild_id = self.unwrap_id(guild)

        data = await self.client.rest.request(GET_GUILD, guild_id=guild_id)
        assert isinstance(data, dict)

        return await self.upsert(data)

    def on_join(self):
        return self.on(GuildEvent.JOIN)

    def on_available(self):
        return self.on(GuildEvent.AVAILABLE)

    def on_receive(self):
        return self.on(GuildEvent.RECEIVE)

    def on_update(self):
        return self.on(GuildEvent.UPDATE)

    def on_delete(self):
        return self.on(GuildEvent.DELETE)

    def on_unavailable(self):
        return self.on(GuildEvent.UNAVAILABLE)

    def get_events(self) -> type[GuildEvent]:
        return GuildEvent

    def get_intents(self) -> WebSocketIntents:
        return WebSocketIntents.GUILDS

    async def process_event(
        self, event: str, shard: ShardWebSocket, payload: JSONData
    ) -> BaseEvent:
        event = self.cast_event(event)

        if event is GuildEvent.JOIN:
            guild = await self.upsert(payload)
            return GuildJoinEvent(shard=shard, payload=payload, guild=guild)

        if event is GuildEvent.AVAILABLE:
            guild = await self.upsert(payload)
            return GuildAvailableEvent(shard=shard, payload=payload, guild=guild)

        if event is GuildEvent.RECEIVE:
            guild = await self.upsert(payload)
            return GuildReceiveEvent(shard=shard, payload=payload, guild=guild)

        if event is GuildEvent.UPDATE:
            guild = await self.upsert(payload)
            return GuildUpdateEvent(shard=shard, payload=payload, guild=guild)

        if event is GuildEvent.DELETE:
            guild = self.pop(payload['id'])
            return GuildDeleteEvent(shard=shard, payload=payload, guild=guild)
