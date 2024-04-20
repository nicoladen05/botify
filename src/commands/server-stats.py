import discord
from discord.ext import commands

# Configure your channels here
GUILD = 803587371152441345
CHANNEL_MEMBERS = 1231167106171666442  # Make sure this is a voice channel


async def get_member_counts(bot):
    guild = discord.utils.get(bot.guilds, id=GUILD)
    members = guild.members

    users = 0
    bots = 0

    for member in members:
        if member.bot:
            bots += 1
        else:
            users += 1

    return users, bots


async def update_channels(bot, counts):
    # update the channel name
    channel = bot.get_channel(CHANNEL_MEMBERS)
    channel_name = f"👥 {counts[0]+counts[1]} | 👤 {counts[0]} | 🤖 {counts[1]}"
    await channel.edit(name=channel_name)


class Stats(commands.Cog):
    def __init__(self, bot):
        print("[COG] Server Stats Cog loaded!")
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()

        member_counts = await get_member_counts(self.bot)
        await update_channels(self.bot, member_counts)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        member_counts = await get_member_counts(self.bot)
        await update_channels(self.bot, member_counts)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        member_counts = await get_member_counts(self.bot)
        await update_channels(self.bot, member_counts)


def setup(bot):
    bot.add_cog(Stats(bot))
