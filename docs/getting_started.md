# Getting Started

## Installation

Installation can be done with `pip`
```
pip install -U snakecord
```

## Examples

```python
import snakecord

TOKEN = ''

client = snakecord.UserClient(TOKEN)


@client.on()
async def message_create(evnt):
    message = evnt.message
    channel = evnt.channel
    if message.content == ".ping":
        await channel.messages.create("Pong!")


client.run_forever()
```