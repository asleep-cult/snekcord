import asyncio
import snakecord
import functools
import unittest
import threading


class SnakecordTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()
        cls.client = snakecord.Client()

        start = functools.partial(cls.client.start, cls.TOKEN)
        cls.thread = threading.Thread(target=start)
        cls.thread.start()

        async def wait():
            await cls.client.wait('guild_create')

        future = asyncio.run_coroutine_threadsafe(wait(), cls.loop)
        future.result()

    @classmethod
    def tearDownClass(cls):
        cls.loop.stop()


def asyncTest(loop=None):
    loop = loop or asyncio.get_event_loop()

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            future = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), loop)
            return future.result()

        return wrapped

    return wrapper
