from __future__ import annotations

import enum
from dataclasses import dataclass

from ...connections.shard import Shard
from ...objects.guild import Guild
from ...states.guild import GuildState
from ...utils.events import EventPusher


@dataclass
class _base_event:
    manager: UserClientManager
    shard: Shard
    payload: dict


class user_client_events(enum.Enum):
    @dataclass
    class application_command_create(_base_event):
        pass

    @dataclass
    class application_command_update(_base_event):
        pass

    @dataclass
    class application_command_delete(_base_event):
        pass

    @dataclass
    class channel_create(_base_event):
        pass

    @dataclass
    class channel_update(_base_event):
        pass

    @dataclass
    class channel_delete(_base_event):
        pass

    @dataclass
    class channel_pins_update(_base_event):
        pass

    @dataclass
    class guild_create(_base_event):
        guild: Guild = None

        def __post_init__(self):
            self.guild = self.manager.guilds.append(self.payload)

    @dataclass
    class guild_update(_base_event):
        pass

    @dataclass
    class guild_delete(_base_event):
        pass

    @dataclass
    class guild_ban_add(_base_event):
        pass

    @dataclass
    class guild_ban_remove(_base_event):
        pass

    @dataclass
    class guild_emojis_update(_base_event):
        pass

    @dataclass
    class guild_integrations_update(_base_event):
        pass

    @dataclass
    class guild_member_add(_base_event):
        pass

    @dataclass
    class guild_member_remove(_base_event):
        pass

    @dataclass
    class guild_member_update(_base_event):
        pass

    @dataclass
    class guild_members_chunk(_base_event):
        pass

    @dataclass
    class guild_role_create(_base_event):
        pass

    @dataclass
    class guild_role_update(_base_event):
        pass

    @dataclass
    class guild_role_delete(_base_event):
        pass

    @dataclass
    class integration_create(_base_event):
        pass

    @dataclass
    class integration_update(_base_event):
        pass

    @dataclass
    class integration_delete(_base_event):
        pass

    @dataclass
    class interaction_create(_base_event):
        pass

    @dataclass
    class invite_create(_base_event):
        pass

    @dataclass
    class invite_delete(_base_event):
        pass

    @dataclass
    class message_create(_base_event):
        pass

    @dataclass
    class message_update(_base_event):
        pass

    @dataclass
    class message_delete(_base_event):
        pass

    @dataclass
    class message_delete_bulk(_base_event):
        pass

    @dataclass
    class message_reaction_add(_base_event):
        pass

    @dataclass
    class message_reaction_remove(_base_event):
        pass

    @dataclass
    class message_reaction_remove_all(_base_event):
        pass

    @dataclass
    class message_reaction_remove_emoji(_base_event):
        pass

    @dataclass
    class presence_update(_base_event):
        pass

    @dataclass
    class typing_state(_base_event):
        pass

    @dataclass
    class user_update(_base_event):
        pass

    @dataclass
    class voice_state_update(_base_event):
        pass

    @dataclass
    class voice_server_update(_base_event):
        pass

    @dataclass
    class webhooks_update(_base_event):
        pass


class UserClientManager(EventPusher):
    handlers = user_client_events

    def __init__(self, *args, **kwargs) -> None:
        self.shard_range = kwargs.pop('shard_range', range(1))
        super().__init__(*args, **kwargs)
        self.shards = {}
        self.token = None
        self.guilds = GuildState(manager=self)

    async def start(self, token: str, *args, **kwargs):
        self.token = token

        for i in self.shard_range:
            self.shards[i] = Shard(self, i)

        for shard in self.shards.values():
            await shard.connect(*args, **kwargs)
