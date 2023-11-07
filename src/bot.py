import discord
from discord.ext import commands

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

asyncio.run(bot.load_extension("commands.ping"))

bot.run(TOKEN)