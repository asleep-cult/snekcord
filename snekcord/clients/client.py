from ..manager import Manager


class Client:
    def __init__(self, token, **kwargs):
        self.manager = Manager(token, **kwargs)

    def on(self, *args, **kwargs):
        return self.manager.on(*args, **kwargs)

    def once(self, *args, **kwargs):
        return self.manager.once(*args, **kwargs)

    def wait(self, *args, **kwargs):
        return self.manager.wait(*args, **kwargs)

    @property
    def rest(self):
        return self.manager.rest

    @property
    def channels(self):
        return self.manager.channels

    @property
    def guilds(self):
        return self.manager.guilds

    @property
    def invites(self):
        return self.manager.invites

    @property
    def stages(self):
        return self.manager.stages

    @property
    def users(self):
        return self.manager.users

    @property
    def members(self):
        for guild in self.guilds:
            yield from guild.members

    @property
    def messages(self):
        for channel in self.channels:
            yield from channel.messages

    @property
    def roles(self):
        for guild in self.guilds:
            yield from guild.roles

    @property
    def emojis(self):
        for guild in self.guilds:
            yield from guild.emojis
