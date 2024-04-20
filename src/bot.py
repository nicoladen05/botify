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
bot.load_extension("commands.server-stats")
bot.load_extension("commands.minecraft-server")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


bot.run(TOKEN)
