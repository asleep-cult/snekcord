from datetime import datetime

__all__ = ('Snowflake',)


class Snowflake(int):
    __slots__ = ()

    SNOWFLAKE_EPOCH = 1420070400000

    TIMESTAMP_SHIFT = 22
    WORKER_ID_SHIFT = 17
    PROCESS_ID_SHIFT = 12

    WORKER_ID_MASK = 0x3E0000
    PROCESS_ID_MASK = 0x1F000
    INCREMENT_MASK = 0xFFF

    @classmethod
    def build(cls, timestamp=None, worker_id=0, process_id=0, increment=0):
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        elif isinstance(timestamp, datetime):
            timestamp = timestamp.timestamp()

        timestamp = int((timestamp * 1000) - cls.SNOWFLAKE_EPOCH)

        return cls((timestamp << cls.TIMESTAMP_SHIFT)
                   | (worker_id << cls.WORKER_ID_SHIFT)
                   | (process_id << cls.PROCESS_ID_SHIFT)
                   | increment)

    @classmethod
    def try_snowflake(cls, obj, *, allow_datetime=False):
        from .objects.baseobject import BaseObject

        if isinstance(obj, BaseObject):
            if isinstance(obj.id, cls):
                return obj.id
            else:
                raise ValueError(f'Failed to convert {obj!r} to a Snowflake')
        elif allow_datetime:
            if isinstance(obj, datetime):
                return cls.build(obj.timestamp())

        try:
            return cls(obj)
        except Exception:
            raise ValueError(f'Failed to convert {obj!r} to a Snowflake')

    @classmethod
    def try_snowflake_many(cls, objs, *, allow_datetime=False):
        return tuple({cls.try_snowflake(obj, allow_datetime=allow_datetime) for obj in objs})

    @property
    def timestamp(self):
        return ((self >> self.TIMESTAMP_SHIFT) + self.SNOWFLAKE_EPOCH) / 1000

    @property
    def worker_id(self):
        return (self & self.WORKER_ID_MASK) >> self.WORKER_ID_SHIFT

    @property
    def process_id(self):
        return (self & self.PROCESS_ID_MASK) >> self.PROCESS_ID_SHIFT

    @property
    def increment(self):
        return self & self.INCREMENT_MASK

    def as_datetime(self):
        return datetime.fromtimestamp(self.timestamp)
