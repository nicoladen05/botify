import discord
from discord.ext import commands

GUILD_ID = 803587371152441345

ROLE_ID = 803933313114308630


class JoinLeave(discord.Cog):
    def __init__(self, bot):
        print("[COG] Join Role Loaded!")
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == GUILD_ID:
            role = member.guild.get_role(ROLE_ID)

            await member.add_roles(role)


def setup(bot):
    bot.add_cog(JoinLeave(bot))
