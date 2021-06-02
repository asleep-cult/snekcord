# snekcord
A work-in-progress Discord API wrapper written in Python.

![Python: >= 3.7](https://img.shields.io/static/v1?label=Python&message=%3E=%203.7&color=yellow)

## Examples
```python
import snekcord

TOKEN = ''

client = snekcord.WebSocketClient(TOKEN)


@client.on()
async def message_create(evt):
    message = evt.message
    channel = evt.channel
    if message.content == '.ping':
        await channel.messages.create(content='Pong!')


client.run_forever()
```

## Discord Server
[![](https://discordapp.com/api/v8/guilds/834890063581020210/widget.png?style=banner1)](https://discord.gg/kAe2m4hdZ7)

## Documentation
Read our documentation [here](https://asleep-cult.github.io/snekcord/).
