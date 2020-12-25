from lib import Client

client = Client()

@client.on
async def guild_create(guild):
    print(guild.emojis)

print('hi')

client.start('NzI5NDI1NjM1MTM0NTM3NzQw.XwIwjw.EJJ6CMSqKRHCezBX9JURIyvVMJU')