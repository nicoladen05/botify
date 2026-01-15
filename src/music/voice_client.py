import logging

import discord
import lavalink


class VoiceClient(discord.VoiceProtocol):
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        if not client.user:
            logging.error("Client user is not set")
            return

        self.client = client
        self.channel = channel
        self.lavalink = lavalink.Client(client.user.id)
        self.lavalink.add_node(
            host="lavalink.serenetia.com",
            port=443,
            password="https://dsc.gg/ajidevserver",
            region="eu",
        )

    async def on_voice_server_update(self, data) -> None:
        await self.lavalink.voice_update_handler(
            {"t": "VOICE_SERVER_UPDATE", "d": data}
        )

    async def on_voice_state_update(self, data) -> None:
        channel_id = data.get["channel_id"]

        if not channel_id:
            await self._destroy()
            return

        self.channel = self.client.get_channel(int(channel_id))
