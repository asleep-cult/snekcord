## snekcord!
```py
import asyncio
import snekcord

client = snekcord.WebSocketClient("Bot <TOKEN>")


@client.messages.on_create()
async def message_create(evt: snekcord.MessageCreateEvent):
    if evt.message.content == 'ping':
        await channel.messages.create(content='pong')


if __name__ == '__main__':
    asyncio.run(client.connect())
```
