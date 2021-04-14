import enum


class VoiceOpcode(enum.IntEnum):
    IDENTIFY = 0
    SELECT_PROTOCOL = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUME = 9
    CLIENT_CONNECT = 12
    CLIENT_DISCONNECT = 13
