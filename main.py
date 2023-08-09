import discord
import json
import datetime
import asyncio
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

def get_token():
    file_path = 'token.secret'
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            return file_content
    except Exception:
        ...

@bot.command()
async def ping(ctx):
    await ctx.send('pong')
    
@bot.command()
async def meuche(ctx):
    await ctx.send('roume')

private_to_public_id = {}

filename = 'data.json'

async def get_messages():
    private_channel = bot.get_channel(1136384711367872603)
    public_channel = bot.get_channel(1138964785841577994)
    async for private_message in private_channel.history():
        public_message_id = private_to_public_id.get(private_message.id)
        if public_message_id is not None:
            public_message = await public_channel.fetch_message(public_message_id)
            await public_message.edit(content=private_message.content)
        else:
            public_message = await public_channel.send(private_message.content)
            private_to_public_id[private_message.id] = public_message.id
            await public_message.add_reaction("✨")
            await public_message.add_reaction("✅")
            await public_message.add_reaction("❌")
    
    private_ids_to_remove = []
    for private_id in private_to_public_id.keys():
        try:
            await private_channel.fetch_message(private_id)
        except discord.NotFound:
            public_message = await public_channel.fetch_message(private_to_public_id[private_id])
            await public_message.delete()
            private_ids_to_remove.append(private_id)
    for private_id in private_ids_to_remove:
        del private_to_public_id[private_id]

    with open(filename, 'w') as file:
        json.dump(private_to_public_id, file)

@bot.command()
async def send_embed(ctx):
    embed = discord.Embed(
        title="Exemple d'Embed",
        description="Ceci est un exemple de message embed.",
        color=discord.Color.blue(),  # Couleur de l'embed (facultatif)
        # timestamp= datetime.datetime.now(),
    )
    await ctx.send(embed=embed)


class BackgroundCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.background_task.start()

    def cog_unload(self):
        self.background_task.cancel()

    @tasks.loop(seconds=1)
    async def background_task(self):
        await get_messages()

@bot.event
async def on_ready():
    await bot.add_cog(BackgroundCog(bot))


if __name__ == "__main__":
    import os
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            private_to_public_id = json.load(file)
            private_to_public_id = {int(key): value for key, value in private_to_public_id.items()}
    bot.run(get_token())