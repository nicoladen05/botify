from discord.ext import commands

class Ping(commands.Cog):
    @commands.command()
    async def ping(self, ctx):
        await ctx.reply("Pong")


async def setup(bot):
    await bot.add_cog(Ping(bot))