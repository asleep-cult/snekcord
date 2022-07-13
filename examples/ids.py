import asyncio

import snekcord

intents = snekcord.WebSocketIntents.GUILDS | snekcord.WebSocketIntents.GUILD_MESSAGES
client = snekcord.WebSocketClient("Bot <TOKEN>", intents=intents)


@client.messages.on_create()
async def message_create(evt: snekcord.MessageCreateEvent):
    assert evt.message.content is not None
    channel_id = evt.channel.unwrap_id()

    if evt.message.content.startswith('!delete'):
        msg_id = evt.message.content.split()[1]
        msg = await client.messages.delete(channel_id, msg_id)

        async with client.messages.create(channel_id) as builder:
            if msg is not None:
                builder.content(f"I've deleted a message saying {msg.content!r}")
            else:
                builder.content(f"I've delete a message with the id {msg_id}")


if __name__ == '__main__':
    asyncio.run(client.connect())
