from discord.ext import commands
import discord

TESTING_GUILDS = ["902614427541590066"]


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="ping",
        description=":clock1: Pings the bot",
        guild_ids=TESTING_GUILDS,
    )
    async def ping(self, ctx):
        ping = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title=":clock1: Pong!",
            description=f"The bots latency is {ping}ms",
            color=discord.Color.blue(),
        )

        await ctx.respond(embed=embed)


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="ban",
        description=":hammer: Bans a user",
        guild_ids=TESTING_GUILDS,
    )
    async def ban(self, ctx, user: discord.Member):
        try:
            user.ban()
        except Exception:
            embed = discord.Embed(
                title=":warning: Failed!",
                description=f"Failed to ban {user}!",
                color=discord.Color.red(),
            )

            await ctx.respond(embed=embed)

        embed = discord.Embed(
            title=":white_check_mark: Success!",
            description=f"Banned {user}!",
            color=discord.Color.green(),
        )

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Ping(bot))
