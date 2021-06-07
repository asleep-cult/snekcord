# Getting Started

## Installation

Installation can be done with `pip`
```
pip install -U snekcord
```

## Examples

```python
import snekcord

TOKEN = ''

client = snekcord.Client(TOKEN)


@client.on()
async def message_create(evt):
    message = evt.message
    channel = evt.channel
    if message.content == ".ping":
        await channel.messages.create("Pong!")


client.loop.create_task(client.login())
client.run_forever()
```
