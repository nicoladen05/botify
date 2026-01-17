import logging

import discord
from discord.ext import commands


class Essentials(commands.Cog):
    def __init__(self, bot):
        logging.info("[COG] Ping Cog Loaded!")
        self.bot = bot

    @discord.app_commands.command(name="ping", description="Get the bots latency")
    async def ping(self, interaction: discord.Interaction):
        ping = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title=":clock1: Pong!",
            description=f"The bots latency is {ping}ms",
            color=discord.Color.blue(),
        )

        await interaction.response.send_message(embed=embed)

    @commands.hybrid_command(name="sync", description="Sync the slash commands")
    @commands.is_owner()
    async def sync(self, ctx):
        logging.info("Syncing slash commands")
        await self.bot.tree.sync()
        await ctx.send("Slash commands synced!")

    @commands.hybrid_command(name="copy_global", description="Sync the slash commands ")
    @commands.is_owner()
    async def sync_debug(self, ctx):
        await self.bot.tree.sync(guild=discord.Object(id=803587371152441345))
        await ctx.send("Copied slash commands to testing guild!")
