from .manager import UserClientManager
from ...utils.events import EventDispatcher


class UserClient(EventDispatcher):
    def __init__(self, token, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.manager = UserClientManager(token, loop=self.loop)
        self.subscribe(self.manager)

    async def start(self, *args, **kwargs) -> None:
        await self.manager.start(*args, **kwargs)

    def run_forever(self, *args, **kwargs):
        self.loop.create_task(self.start(*args, **kwargs))
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            return
