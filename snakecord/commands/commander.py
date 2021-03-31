class CommandInvokeEvent:
    def __init__(self, commander, message, parser, prefix):
        self.commander = commander
        self.message = message
        self.parser = parser
        self.prefix = prefix
        self.args = []
        self.kwargs = {}
        self.command = None
        self.invoker = self.message.author
        self.channel = self.message.channel
        self.guild = self.message.guild
        self.send = self.channel.send

        try:
            cmd = parser.get_argument()
        except EOFError:
            return
        for name, command in commander.commands.items():
            if cmd == name:
                self.command = command

    @property
    def channel(self):
        return self.message.channel

    @property
    def invoker(self):
        return self.message.author

    @property
    def guild(self):
        return self.message.guild
    
    @property
    def send(self):
        return self.channel.send
    
    def invoke(self):
        if not self.command:
            return
        self.command.invoke(self)

class CommandInvokeHandler:
    def __init__(self, name):
        self.name = name
    
    def __call__(self, commander, evnt, *args, **kwargs):
        self.commander = commander
        self.evnt = evnt
        self.args = args
        self.kwargs = kwargs
        return self