import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix='!')


@client.command(hidden=True)
async def load (ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command(hidden=True)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.getenv('TOKEN_CONNECTION'))