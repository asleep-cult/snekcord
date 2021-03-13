# snakecord
A WIP Discord API wrapper that aims to cover the full API. 

```python
import snakecord

TOKEN = ''

client = snakecord.Client()


@client.events.on
async def message_create(event):
    message = event.message

    if message.content == '!ping':
        shard = message.guild.shard
        await message.channel.send(f'Latency: {shard.websocket.latency}')


client.start(TOKEN)
```