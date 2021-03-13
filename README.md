# snakecord
A WIP Discord API wrapper that aims to cover the full API. 

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
