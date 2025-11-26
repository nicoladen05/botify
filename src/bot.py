import asyncio
import os

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

INTENTS = discord.Intents.default()
INTENTS.members = True

bot = discord.Bot(intents=INTENTS)

# Commands
bot.load_extension("commands.essentials")
bot.load_extension("commands.music")
bot.load_extension("stats.server-stats")
bot.load_extension("stats.minecraft-stats")
bot.load_extension("tools.default_role")
bot.load_extension("commands.minecraft-restart")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="for /help")
    )


bot.run(TOKEN)
