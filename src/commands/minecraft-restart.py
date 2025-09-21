import discord
import requests
import subprocess
from io import StringIO
from discord.ext import commands

TESTING_GUILDS = ["902614427541590066", "803587371152441345"]

ALLOWED_USERS = [
    458263932839395348, # Nico
    719572878051377224, # Olli
    556397529223135233, # Jakob
    411781099069374465 # Mathis
]

LOG_COMMAND = "podman compose -f ~/docker/minecraft/compose.yml logs"
RESTART_COMMAND  = "podman compose -f ~/docker/minecraft/compose.yml up -d --force-recreate"


class MinecraftRestart(commands.Cog):
    def __init__(self, bot):
        print("[COG] Minecraft Restart Loaded!")
        self.bot = bot

    def upload_to_hastebin(self, content):
        response = requests.post("https://hastebin.com/documents", data=content.encode())
        response.raise_for_status()
        key = response.json()['key']
        return f"https://hastebin.com/{key}"

    @commands.slash_command(
        name="minecraft",
        description="Minecraft Server commands",
        guild_ids=TESTING_GUILDS,
    )
    async def join(self, ctx, arg):
        if not ctx.author.id in ALLOWED_USERS:
            await ctx.respond(f"{ctx.author.id} You are not allowed to run this command")
            return

        match arg:
            case "logs":
# Run SSH command
                result = subprocess.run(
                    ["ssh", "nico@server.nicoladen.dev", LOG_COMMAND],
                    capture_output=True,
                    text=True
                )

                full_output = result.stdout + result.stderr

                trimmed_output = full_output[-1990:]
                
                await ctx.respond(
                    f"```\n{trimmed_output}\n```",
                    ephemeral=True
                )

            case "restart":
                await ctx.respond("Restarting server...", ephemeral=True)
                subprocess.run(
                    ["ssh", "nico@server.nicoladen.dev", RESTART_COMMAND],
                )
                await ctx.followup.send("Server Restarted ✅", ephemeral=True)

            case _:
                ctx.respond("Invalid Argument")

def setup(bot):
    bot.add_cog(MinecraftRestart(bot))
