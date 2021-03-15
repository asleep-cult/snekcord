class CommandInvokeEvent:
    def __init__(self, commander, message, parser, prefix):
        self.commander = commander
        self.message = message
        self.parser = parser
        self.prefix = prefix
        self.args = []
        self.kwargs = {}
