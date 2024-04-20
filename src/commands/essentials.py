import discord
from discord.ext import commands

TESTING_GUILDS = ["902614427541590066", "803587371152441345"]


class Ping(commands.Cog):
    def __init__(self, bot):
        print("[COG] Ping Cog Loaded!")
        self.bot = bot

    @commands.slash_command(
        name="ping",
        description="Pings the bot",
        guild_ids=TESTING_GUILDS,
    )
    async def join(self, ctx):
        ping = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title=":clock1: Pong!",
            description=f"The bots latency is {ping}ms",
            color=discord.Color.blue(),
        )

        await ctx.respond(embed=embed)


#
# class Management(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#
#     @commands.slash_command(
#         name="ban",
#         description="Bans a user",
#         guild_ids=TESTING_GUILDS,
#     )
#     async def ban(self, ctx, user: discord.Member):
#         await user.ban()
#
#         embed = discord.Embed(
#             title=":white_check_mark: Success!",
#             description=f"Banned {user}!",
#             color=discord.Color.green(),
#         )
#
#         await ctx.respond(embed=embed)
#
#     async def kick(self, ctx, user: discord.Member):
#         await user.kick()
#
#         embed = discord.Embed(
#             title=":white_check_mark: Success!",
#             description=f"Kicked {user}!",
#             color=discord.Color.green(),
#         )
#
#         await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Ping(bot))
    # bot.add_cog(Management(bot))
