import asyncio

import snekcord

intents = snekcord.WebSocketIntents.GUILDS | snekcord.WebSocketIntents.GUILD_MESSAGES
client = snekcord.WebSocketClient("Bot <TOKEN>", intents=intents)


@client.messages.on_create()
async def message_create(evt: snekcord.MessageCreateEvent):
    channel = await evt.channel.unwrap_as(snekcord.TextChannel)

    if evt.message.content == 'ping':
        await channel.messages.create(content='pong')


if __name__ == '__main__':
    asyncio.run(client.connect())
