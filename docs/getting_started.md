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

client = snekcord.UserClient(TOKEN)


@client.on()
async def message_create(evnt):
    message = evnt.message
    channel = evnt.channel
    if message.content == ".ping":
        await channel.messages.create("Pong!")


client.run_forever()
```