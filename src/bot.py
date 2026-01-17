import logging
import os
from typing import override

import discord
from discord.ext import commands
from dotenv import load_dotenv
from rich.logging import RichHandler

from src.commands.essentials import Essentials
from src.music.music import Music
from src.stats.minecraft_stats import MinecraftStatus
from src.stats.server_stats import Stats
from src.tools.default_role import DefaultRole

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler(rich_tracebacks=True)],
)

_ = load_dotenv()

TOKEN = os.getenv("BOT_TOKEN", "")
if not TOKEN:
    logging.fatal("No bot token found in .env file")


class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents):
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self) -> None:
        assert self.user is not None
        logging.info(f"Logged in as {self.user}")

    @override
    async def setup_hook(self) -> None:
        await self.add_cog(Essentials(self))
        await self.add_cog(DefaultRole(self))
        await self.add_cog(Stats(self))
        await self.add_cog(MinecraftStatus(self))
        await self.add_cog(Music(self))


INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True

bot = Bot(intents=INTENTS)

bot.run(TOKEN)
