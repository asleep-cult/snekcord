from .manager import UserClientManager
from ...utils.events import EventDispatcher


class UserClient(EventDispatcher):
    def __init__(self, token, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.manager = UserClientManager(token, loop=self.loop)
        self.subscribe(self.manager)

    async def start(self, *args, **kwargs) -> None:
        await self.manager.start(*args, **kwargs)
