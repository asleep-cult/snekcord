import enum


class ShardOpcode(enum.IntEnum):
    DISPATCH = 0  # Discord -> Shard
    HEARTBEAT = 1  # Discord <-> Shard
    IDENTIFY = 2  # Discord <- Shard
    PRESENCE_UPDATE = 3  # Discord -> Shard
    VOICE_STATE_UPDATE = 4  # Discord -> Shard
    VOICE_SERVER_PING = 5  # Discord ~ Shard
    RESUME = 6  # Discord <- Shard
    RECONNECT = 7  # Discord -> Shard
    REQUEST_GUILD_MEMBERS = 8  # Discord <- Shard
    INVALID_SESSION = 9  # Discord -> Shard
    HELLO = 10  # Discord -> Shard
    HEARTBEAT_ACK = 11  # Discord -> Shard
