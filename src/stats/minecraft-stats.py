from discord.ext import commands, tasks
from mcstatus import JavaServer

STATUS_CHANNEL = 1231197975313911848

# Make sure to include the port
SERVER_IP = "mc.nicoladen.dev:25565"


def get_server_stats():
    server = JavaServer.lookup(SERVER_IP)

    try:
        status = server.status()
    except ConnectionRefusedError:
        return False, 0

    return True, status.players.online


class Misc(commands.Cog):
    def __init__(self, bot):
        print("[COG] Minecraft Cog loaded!")
        self.bot = bot
        self.channel = self.bot.get_channel(STATUS_CHANNEL)
        self.players = None
        self.online = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.bot.get_channel(STATUS_CHANNEL)
        self.update_channel.start()

    @tasks.loop(seconds=60)
    async def update_channel(self):
        online, players = get_server_stats()

        if online == self.online and players == self.players:
            return

        if online:
            channel_name = f"⛏️ 🟢 Online | 👤 {players}"
        else:
            channel_name = "⛏️ 🔴 Offline"

        await self.channel.edit(name=channel_name)

        if self.channel.name == channel_name:  # Channel name got updated sucessfully
            self.online = online
            self.players = players


def setup(bot):
    bot.add_cog(Misc(bot))
