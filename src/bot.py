import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Bot(intents=intents)

# Commands
client.load_extension("commands.essentials")


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")


client.run(TOKEN)
