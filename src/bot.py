import discord
import os
from discord.ext import commands

token = ""
prefix = "*"
f = open("token.key", "r")
token = f.read().replace("\n", "")
f.close()

bot = commands.Bot(command_prefix=prefix)
bot.remove_command("help")
@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    bot.load_extension('cogs.music')
    bot.load_extension('cogs.role')
    bot.load_extension('cogs.komutlar')
    activity = discord.Game(name=f"{prefix}help or {prefix}h")
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    
    

bot.run(token)
