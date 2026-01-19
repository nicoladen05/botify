import logging

import a2s
from discord.ext import commands, tasks

STATUS_CHANNEL = 1462416367364870349
SERVER_IP = "server.nicoladen.dev"
SERVER_PORT = 5521


def get_server_stats():
    try:
        info = a2s.info((SERVER_IP, SERVER_PORT))
        return True, info.player_count
    except Exception:
        logging.error(f"Failed to get Hytale server stats")
        return False, 0


class HytaleStatus(commands.Cog):
    def __init__(self, bot):
        logging.info("[COG] Hytale Cog loaded!")
        self.bot = bot
        self.channel = self.bot.get_channel(STATUS_CHANNEL)
        self.online = None
        self.player_count = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.bot.get_channel(STATUS_CHANNEL)
        if not self.channel:
            logging.warning(f"Hytale status channel {STATUS_CHANNEL} not found.")
        self.update_channel.start()

    @tasks.loop(seconds=60)
    async def update_channel(self):
        online, player_count = get_server_stats()

        if online == self.online and player_count == self.player_count:
            return

        if self.channel is None:
            self.channel = self.bot.get_channel(STATUS_CHANNEL)
            if self.channel is None:
                return

        if online:
            channel_name = f"🗡️ 🟢 Online | 👤 {player_count}"
        else:
            channel_name = "🗡️ 🔴 Offline"

        try:
            await self.channel.edit(name=channel_name)
            if self.channel.name == channel_name:
                self.online = online
        except Exception as e:
            logging.error(f"Failed to update Hytale channel name: {e}")
