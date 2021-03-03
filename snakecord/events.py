import logging

from . import logger


class EventHandler:
    def __init__(self, client):
        log_handler = logger.Handler(self)
        for log in logger.LOGGERS:
            log.addHandler(log_handler)

        handlers = (
            self.channel_create,
            self.channel_update,
            self.channel_delete,
            self.channel_cache,
            self.channel_pins_update,
            self.guild_create,
            self.guild_update,
            self.guild_delete,
            self.guild_ban_add,
            self.invite_create,
            self.message_create,
            self.log_info,
            self.log_critical,
            self.guild_cache,
            self.member_cache,
            self.user_cache,
        )

        self.handlers = {
            handler.__name__.lower(): handler for handler in handlers
        }
        self.listeners = {
            handler.__name__.lower(): [] for handler in handlers
        }

        for name, listeners in self.listeners.items():
            try:
                attr = getattr(self.client, name)
            except AttributeError:
                continue
            listeners.append(attr)

        self.client = client
        self.loop = self.client.loop
        self.formatter = logging.Formatter(
            '[%(name)s] [%(cls)s] [%(asctime)s] %(message)s'
        )

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
        return func

    def _call_listeners(self, name, *args):
        for listener in self.listeners[name]:
            self.loop.create_task(listener(*args))

    def channel_create(self, payload):
        channel = self.client.channels._add(payload.data)
        self._call_listeners('channel_create', channel)

    def channel_update(self, payload):
        channel = self.client.channels._add(payload.data)
        self._call_listeners('channel_update', channel)

    def channel_delete(self, payload):
        channel_id = payload.data['id']
        channel = self.client.channels.pop(channel_id)
        if channel is not None:
            self._call_listeners('channel_delete', channel)

    def channel_cache(self, channel):
        self._call_listeners('channel_cache', channel)

    def channel_pins_update(self, payload):
        channel_id = payload.data['channel_id']
        channel = self.client.channels.get(channel_id)
        if channel is not None:
            channel.last_pin_timestamp = payload['last_pin_timestamp']
            self._call_listeners('channel_pins_update', channel)

    def guild_create(self, payload):
        guild = self.client.guilds._add(payload.data)
        self._call_listeners('guild_create', guild)

    def guild_update(self, payload):
        guild = self.client.guilds._add(payload.data)
        self._call_listeners('guild_update', guild)

    def guild_delete(self, payload):
        guild_id = payload.data['id']
        guild = self.client.guilds.pop(guild_id)
        if guild is not None:
            self._call_listeners('guild_delete', guild)

    def guild_ban_add(self, payload):
        guild_id = payload.data['guild_id']
        guild = self.client.guilds.get(guild_id)
        if guild is not None:
            member_id = payload.data['id']
            member = guild.members.pop(member_id)
            self._call_listeners('guild_ban_add', member)

    def invite_create(self, payload):
        invite = self.client.invites._add(payload.data)
        self._call_listeners('invite_create', invite)

    def message_create(self, payload):
        data = payload.data
        channel = self.client.channels.get(data.get('channel_id'))
        if channel is not None:
            message = channel.messages._add(data)
            self._call_listeners('message_create', message)

    def log_info(self, record):
        fmt = self.formatter.format(record)
        self._call_listeners('log_info', fmt, record)

    def log_critical(self, record):
        fmt = self.formatter.format(record)
        self._call_listeners('log_critical', fmt, record)

    def guild_cache(self, guild):
        self._call_listeners('guild_cache', guild)

    def member_cache(self, member):
        self._call_listeners('member_cache', member)

    def user_cache(self, user):
        self._call_listeners('user_cache', user)
