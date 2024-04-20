import discord
from discord.ext import commands

# Configure your channels here
CHANNELS = ["839429097162670110", "839429100167102484", "839429103139553330"]


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Stats())
