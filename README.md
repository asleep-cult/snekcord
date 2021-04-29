# snakecord
A work-in-progress Discord API wrapper written in Python.

![Python: >= 3.7](https://img.shields.io/static/v1?label=Python&message=%3E=%203.7&color=yellow)

## Examples
```python
import snakecord

TOKEN = ''

client = snakecord.UserClient(TOKEN)


@client.on()
async def message_create(evnt):
    message = evnt.message
    if message.content == '.ping':
        await message.channel.send('Pong!')


client.run_forever()
```

## Discord Server
[![](https://discordapp.com/api/v8/guilds/834890063581020210/widget.png?style=banner1)](https://discord.gg/kAe2m4hdZ7)

