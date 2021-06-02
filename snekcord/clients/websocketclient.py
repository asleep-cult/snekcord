from .client import Client


class WebSocketClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
