# Snakecord
A work-in-progress Discord API wrapper written in Python.

![Python: >= 3.7](https://img.shields.io/static/v1?label=Python&message=%3E=%203.7&color=yellow)

## Examples
```python
import snakecord

TOKEN = ''

client = snakecord.Client()


@client.on()
async def message_create(evnt):
    message = evnt.message
    if message.content == '.ping':
        await message.channel.send('Pong!')


client.start(TOKEN)
```
