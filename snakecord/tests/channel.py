import unittest
from snakecord.tests.utils import SnakecordTestCase, asyncTest


class TestTextChannelMethodsAsync(SnakecordTestCase):
    TOKEN = None
    TEXT_CHANNEL_ID = None
    PARENT_ID = None

    @asyncTest()
    async def test_edit_name(self):
        channel = self.client.channels.get(self.TEXT_CHANNEL_ID)
        await channel.edit(name='test-channel-name')
        self.assertEqual(channel.name, 'test-channel-name')

    # test_edit_type

    @asyncTest()
    async def test_edit_position(self):
        channel = self.client.channels.get(self.TEXT_CHANNEL_ID)
        await channel.edit(position=3)
        self.assertEqual(channel.position, 3)

    @asyncTest()
    async def test_edit_topic(self):
        channel = self.client.channels.get(self.TEXT_CHANNEL_ID)
        await channel.edit(topic='Test channel topic')
        self.assertEqual(channel.topic, 'Test channel topic')

    @asyncTest()
    async def test_edit_nsfw(self):
        channel = self.client.channels.get(self.TEXT_CHANNEL_ID)
        await channel.edit(nsfw=True)
        self.assertTrue(channel.nsfw)

    @asyncTest()
    async def test_edit_slowmode(self):
        channel = self.client.channels.get(self.TEXT_CHANNEL_ID)
        await channel.edit(slowmode=10)
        self.assertEqual(channel.slowmode, 10)

    @asyncTest()
    async def test_edit_parent(self):
        channel = self.client.channels.get(self.TEXT_CHANNEL_ID)
        await channel.edit(parent=self.PARENT_ID)
        self.assertEqual(channel.parent.id, self.PARENT_ID)

    @asyncTest()
    async def test_delete(self):
        channel = self.client.channels.get(self.TEXT_CHANNEL_ID)
        await channel.delete()
        self.assertNotIn(channel, self.client.channels)


if __name__ == '__main__':
    unittest.main()
