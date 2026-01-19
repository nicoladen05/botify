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

    @discord.app_commands.command(name="help", description="Get help with the bot")
    async def help(self, interaction: discord.Interaction):
        OWNER_ONLY_COMMANDS = ["sync", "copy_global"]

        command_groups = {}

        for command in discord.app_commands.CommandTree.walk_commands(self.bot.tree):
            if (
                isinstance(command, discord.app_commands.Group)
                or command.qualified_name in OWNER_ONLY_COMMANDS
            ):
                continue

            # Get parent group name or use "General" for top-level commands
            parent = (
                command.parent.qualified_name.title() if command.parent else "General"
            )

            if parent not in command_groups:
                command_groups[parent] = []

            # Format command name and description
            cmd_name = command.qualified_name
            cmd_desc = command.description or "No description"
            command_groups[parent].append(f"**/{cmd_name}** - {cmd_desc}")

        embed = discord.Embed(
            title=":books: Available Commands",
            color=discord.Color.blue(),
        )

        for group_name, commands_list in sorted(command_groups.items()):
            embed.add_field(
                name=group_name, value="\n".join(commands_list), inline=False
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
