import logging


class Handler(logging.Handler):
    def __init__(self, event_handler, *args, **kwargs):
        self.event_handler = event_handler
        super().__init__(logging.DEBUG)

    def emit(self, record: logging.LogRecord):
        func = getattr(
            self.event_handler,
            'log_%s' % record.levelname.lower()
        )
        if func is not None:
            loop = self.event_handler.loop
            loop.call_soon_threadsafe(func, record)


NAME = __package__ + '.' if __package__ is not None else ''
CONNECTION_LOGGER = logging.getLogger(NAME + 'connection')

LOGGERS = {
    CONNECTION_LOGGER
}
