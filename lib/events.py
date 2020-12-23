class EventHandler:
    def __init__(self, client):
        handlers = (
            self.guild_create,
        )
        self.handlers = {handler.__name__.lower(): handler for handler in handlers}
        self.listeners = {handler.__name__.lower(): [] for handler in handlers}
        self._client = client

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

    def guild_create(self, payload):
        guild = self._client.guilds.add(payload.data)
        self._call_listeners('guild_create', guild)
