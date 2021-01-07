import logging


class LogHandler(logging.StreamHandler):
    def __init__(self, event_handler):
        super().__init__()
        self.event_handler = event_handler

    def emit(self, record: logging.LogRecord):
        if record.levelno == logging.INFO:
            self.event_handler.log_info(record)
        elif record.levelno == logging.CRITICAL:
            self.event_handler.log_critical(record)


class EventHandler:
    def __init__(self, client):
        handlers = (
            self.log_info,
            self.log_critical,
            self.invite_create,
            self.message_create,
            self.guild_create
        )
        self.handlers = {
            handler.__name__.lower(): handler for handler in handlers
        }
        self.listeners = {
            handler.__name__.lower(): [] for handler in handlers
        }
        self._client = client
        self.formatter = logging.Formatter(
            '[%(name)s] [%(cls)s] [%(asctime)s] %(message)s'
        )

    def getLogger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(LogHandler(self))
        return logger

    def dispatch(self, payload):
        name = payload.event_name.lower()
        handler = self.handlers.get(name)
        if handler is not None:
            handler(payload)

    def add_listener(self, func):
        name = func.__name__.lower()
        listeners = self.listeners.get(name)
        if listeners is None:
            raise Exception
        listeners.append(func)

    def _call_listeners(self, name, *args):
        for listener in self.listeners[name]:
            self._client.loop.create_task(listener(*args))

    def invite_create(self, payload):
        invite = self._client.invites._add(payload.data)
        self._call_listeners('invite_create', invite)

    def message_create(self, payload):
        data = payload.data
        channel = self._client.channels.get(data.get('channel_id'))
        if channel is not None:
            message = channel.messages._add(data)
            self._call_listeners('message_create', message)

    def guild_create(self, payload):
        guild = self._client.guilds._add(payload.data)
        self._call_listeners('guild_create', guild)

    def log_info(self, record):
        fmt = self.formatter.format(record)
        self._call_listeners('log_info', fmt, record)

    def log_critical(self, record):
        fmt = self.formatter.format(record)
        self._call_listeners('log_critical', fmt, record)
