import logging
import socket

from discord.ext import commands, tasks

STATUS_CHANNEL = 1462416367364870349
SERVER_IP = "server.nicoladen.dev"
SERVER_PORT = 5520


def get_server_stats():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    try:
        # Hytale doesn't have a known query protocol yet.
        # We send a dummy packet. If the port is closed (ICMP Port Unreachable),
        # we might get a ConnectionRefusedError (depending on OS/networking).
        # This is a best-effort "is it there" check for UDP.
        sock.sendto(b"\x00", (SERVER_IP, SERVER_PORT))
        # We don't expect a reply since we don't know the protocol.
        # If we didn't get an immediate error, we assume it's "up" or at least filtered.
        return True, 0
    except ConnectionRefusedError:
        return False, 0
    except Exception as e:
        logging.warning(f"Error checking Hytale server: {e}")
        return False, 0
    finally:
        sock.close()


class HytaleStatus(commands.Cog):
    def __init__(self, bot):
        logging.info("[COG] Hytale Cog loaded!")
        self.bot = bot
        self.channel = self.bot.get_channel(STATUS_CHANNEL)
        self.online = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.bot.get_channel(STATUS_CHANNEL)
        if not self.channel:
            logging.warning(f"Hytale status channel {STATUS_CHANNEL} not found.")
        self.update_channel.start()

    @tasks.loop(seconds=60)
    async def update_channel(self):
        online, _ = get_server_stats()

        if online == self.online:
            return

        if self.channel is None:
            self.channel = self.bot.get_channel(STATUS_CHANNEL)
            if self.channel is None:
                return

        if online:
            channel_name = "🗡️ 🟢 Online"
        else:
            channel_name = "🗡️ 🔴 Offline"

        try:
            await self.channel.edit(name=channel_name)
            if self.channel.name == channel_name:
                self.online = online
        except Exception as e:
            logging.error(f"Failed to update Hytale channel name: {e}")
