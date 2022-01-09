## snekcord!
```py
import asyncio
import snekcord


class MessageHandler(snekcord.EventHandler):
    async def ping(self, evt: snekcord.MessageCreateEvent):
        if evt.message.content == 'ping':
            await evt.channel.message.create(content='pong')


async def main():
    client = snekcord.WebSocketClient('Bot <TOKEN>')

    listener = client.create_message_listener(direct_messages=True)
    listener.add_handler(MessageHandler())

    await client.connect()


asyncio.run(main())
```
