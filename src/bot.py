import os

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

INTENTS = discord.Intents.default()

bot = discord.Bot(intents=INTENTS)

# Commands
bot.load_extension("commands.essentials")
bot.load_extension("commands.music")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


bot.run(TOKEN)
