import logging
from typing import cast

import a2s
from discord import VoiceChannel
from discord.ext import commands, tasks

STATUS_CHANNEL = 1462416367364870349
SERVER_IP = "server.nicoladen.dev"
SERVER_PORT = 5521


def get_server_stats() -> tuple[bool, int]:
    try:
        info = a2s.info((SERVER_IP, SERVER_PORT))
        return True, cast(int, info.player_count)
    except Exception:
        return False, 0


class HytaleStatus(commands.Cog):
    bot: commands.Bot
    channel: VoiceChannel | None
    online: bool | None
    player_count: int | None

    def __init__(self, bot: commands.Bot) -> None:
        logging.info("[COG] Hytale Cog loaded!")
        self.bot = bot
        self.channel = None
        self.online = None
        self.player_count = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        channel = self.bot.get_channel(STATUS_CHANNEL)
        if isinstance(channel, VoiceChannel):
            self.channel = channel
        else:
            self.channel = None
            logging.warning(f"Hytale status channel {STATUS_CHANNEL} not found.")
        _ = self.update_channel.start()

    @tasks.loop(seconds=60)
    async def update_channel(self) -> None:
        online, player_count = get_server_stats()

        if online == self.online and player_count == self.player_count:
            return

        if self.channel is None:
            channel = self.bot.get_channel(STATUS_CHANNEL)
            if isinstance(channel, VoiceChannel):
                self.channel = channel
            else:
                return

        if online:
            channel_name = f"🗡️ 🟢 Online | 👤 {player_count}"
        else:
            channel_name = "🗡️ 🔴 Offline"

        try:
            _ = await self.channel.edit(name=channel_name)
            if self.channel.name == channel_name:
                self.online = online
                self.player_count = player_count
        except Exception as e:
            logging.error(f"Failed to update Hytale channel name: {e}")
