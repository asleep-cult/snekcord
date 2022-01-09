from datetime import datetime

__all__ = ('Snowflake',)

_SNOWFLAKE_EPOCH = 1420070400000

_TIMESTAMP_SHIFT = 22
_WORKER_ID_SHIFT = 17
_PROCESS_ID_SHIFT = 12

_WORKER_ID_MASK = 0x3E0000
_PROCESS_ID_MASK = 0x1F000
_INCREMENT_MASK = 0xFFF


class Snowflake(int):
    @classmethod
    def build(cls, timestamp=None, worker_id=0, process_id=0, increment=0):
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        elif isinstance(timestamp, datetime):
            timestamp = timestamp.timestamp()

        timestamp = int((timestamp * 1000) - _SNOWFLAKE_EPOCH)

        return cls(
            (timestamp << _TIMESTAMP_SHIFT)
            | (worker_id << _WORKER_ID_SHIFT)
            | (process_id << _PROCESS_ID_SHIFT)
            | increment
        )

    @property
    def timestamp(self):
        return ((self >> _TIMESTAMP_SHIFT) + _SNOWFLAKE_EPOCH) / 1000

    @property
    def worker_id(self):
        return (self & _WORKER_ID_MASK) >> _WORKER_ID_SHIFT

    @property
    def process_id(self):
        return (self & _PROCESS_ID_MASK) >> _PROCESS_ID_SHIFT

    @property
    def increment(self):
        return self & _INCREMENT_MASK

    def to_datetime(self):
        return datetime.fromtimestamp(self.timestamp)
