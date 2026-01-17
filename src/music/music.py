import logging
import re

import discord
import lavalink
from discord import app_commands
from discord.ext import commands
from lavalink.errors import ClientError
from lavalink.events import QueueEndEvent, TrackEndEvent, TrackStartEvent
from lavalink.server import LoadType

LAVALINK_HOST = "lavalinkv4.serenetia.com"
LAVALINK_PORT = 443
LAVALINK_PASSWORD = "https://dsc.gg/ajidevserver"

url_rx = re.compile(r"https?://(?:www\.)?.+")


class LavalinkVoiceClient(discord.VoiceProtocol):
    """
    Custom VoiceProtocol for handling external voice sending via Lavalink.
    """

    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.guild_id = channel.guild.id
        self._destroyed = False

        if not hasattr(self.client, "lavalink"):
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                host=LAVALINK_HOST,
                port=LAVALINK_PORT,
                password=LAVALINK_PASSWORD,
                region="us",
                name="default-node",
                ssl=True,
            )

        self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {"t": "VOICE_SERVER_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        channel_id = data["channel_id"]

        if not channel_id:
            await self._destroy()
            return

        self.channel = self.client.get_channel(int(channel_id))

        lavalink_data = {"t": "VOICE_STATE_UPDATE", "d": data}

        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(
        self,
        *,
        timeout: float,
        reconnect: bool,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(
            channel=self.channel, self_mute=self_mute, self_deaf=self_deaf
        )

    async def disconnect(self, *, force: bool = False) -> None:
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        if not force and not player.is_connected:
            return

        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        await self._destroy()

    async def _destroy(self):
        self.cleanup()

        if self._destroyed:
            return

        self._destroyed = True

        try:
            await self.lavalink.player_manager.destroy(self.guild_id)
        except ClientError:
            pass


class Music(commands.Cog):
    def __init__(self, bot):
        logging.info("[COG] Music Cog Loaded!")
        self.bot = bot

        if not hasattr(bot, "lavalink"):
            bot.lavalink = lavalink.Client(bot.user.id)
            bot.lavalink.add_node(
                host=LAVALINK_HOST,
                port=LAVALINK_PORT,
                password=LAVALINK_PASSWORD,
                region="us",
                name="default-node",
                ssl=True,
            )

        self.lavalink: lavalink.Client = bot.lavalink
        self.lavalink.add_event_hooks(self)

    async def _check_is_in_guild(self, interaction: discord.Interaction) -> bool:
        if isinstance(interaction.user, discord.Member):
            return True

        await interaction.response.send_message(
            embed=discord.Embed(
                title=":x: Error!",
                description="This command can only be used in a server.",
                color=0xFF0000,
            ),
            ephemeral=True,
        )
        return False

    async def ensure_voice(
        self, interaction: discord.Interaction, should_connect: bool = False
    ):
        """
        Ensures the user is in a voice channel and the bot can connect if needed.
        Returns the player if successful, None otherwise.
        """
        if not await self._check_is_in_guild(interaction):
            return None

        assert interaction.guild is not None
        assert interaction.channel is not None
        assert isinstance(interaction.user, discord.Member)

        player = self.bot.lavalink.player_manager.create(interaction.guild.id)

        voice_client = interaction.guild.voice_client

        if not interaction.user.voice or not interaction.user.voice.channel:
            if voice_client is not None:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title=":x: Error!",
                        description="You need to join my voice channel first.",
                        color=0xFF0000,
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title=":x: Error!",
                        description="You are not in a voice channel.",
                        color=0xFF0000,
                    ),
                    ephemeral=True,
                )
            return None

        voice_channel = interaction.user.voice.channel

        if voice_client is None:
            if not should_connect:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title=":x: Error!",
                        description="I'm not playing music.",
                        color=0xFF0000,
                    ),
                    ephemeral=True,
                )
                return None

            permissions = voice_channel.permissions_for(interaction.guild.me)

            if not permissions.connect or not permissions.speak:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title=":x: Error!",
                        description="I need the `CONNECT` and `SPEAK` permissions.",
                        color=0xFF0000,
                    ),
                    ephemeral=True,
                )
                return None

            if voice_channel.user_limit > 0:
                if (
                    len(voice_channel.members) >= voice_channel.user_limit
                    and not interaction.guild.me.guild_permissions.move_members
                ):
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title=":x: Error!",
                            description="Your voice channel is full!",
                            color=0xFF0000,
                        ),
                        ephemeral=True,
                    )
                    return None

            player.store("channel", interaction.channel.id)
            await voice_channel.connect(cls=LavalinkVoiceClient)
        elif (
            isinstance(voice_client.channel, discord.VoiceChannel)
            and voice_client.channel.id != voice_channel.id
        ):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=":x: Error!",
                    description="You need to be in my voice channel.",
                    color=0xFF0000,
                ),
                ephemeral=True,
            )
            return None

        return player

    @lavalink.listener(TrackStartEvent)
    async def on_track_start(self, event: TrackStartEvent):
        guild_id = event.player.guild_id
        channel_id = event.player.channel_id
        guild = self.bot.get_guild(guild_id)

        if not guild:
            return await self.lavalink.player_manager.destroy(guild_id)

        channel = guild.get_channel(channel_id)

        if channel:
            track = event.track
            track_length_seconds = track.duration / 1000
            track_minutes = track_length_seconds // 60
            track_seconds = track_length_seconds % 60
            track_length = f"{track_minutes:02.0f}:{track_seconds:02.0f}"

            embed = discord.Embed(
                title=":play_pause: Now Playing",
                description=f"{track.author} - {track.title}\n{track_length}",
                color=0x00FF00,
            )

            if track.artwork_url:
                embed.set_thumbnail(url=track.artwork_url)

            await channel.send(embed=embed)

    @lavalink.listener(QueueEndEvent)
    async def on_queue_end(self, event: QueueEndEvent):
        guild_id = event.player.guild_id
        guild = self.bot.get_guild(guild_id)

        if guild is not None:
            await guild.voice_client.disconnect(force=True)

    @app_commands.command(name="join", description="Joins your voice channel")
    async def join(self, interaction: discord.Interaction):
        player = await self.ensure_voice(interaction, should_connect=True)
        if player is None:
            return

        assert isinstance(interaction.user, discord.Member)

        if (
            interaction.user.voice is not None
            and interaction.user.voice.channel is not None
        ):
            voice_channel = interaction.user.voice.channel

            embed = discord.Embed(
                title=":white_check_mark: Success!",
                description=f"Joined {voice_channel.name}",
                color=0x00FF00,
            )
        else:
            embed = discord.Embed(
                title=":x: Error!",
                description="You are not in a voice channel",
                color=0xFF0000,
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play", description="Plays a song")
    @app_commands.describe(search="The song to search for or URL to play")
    async def play(self, interaction: discord.Interaction, search: str):
        player = await self.ensure_voice(interaction, should_connect=True)
        if player is None:
            return

        await interaction.response.defer()

        # Remove leading and trailing <>
        query = search.strip("<>")

        # If not a URL, search YouTube
        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if results.load_type == LoadType.EMPTY:
            embed = discord.Embed(
                title=":x: Error!",
                description="I couldn't find any tracks for that query.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed)
            return
        elif results.load_type == LoadType.ERROR:
            embed = discord.Embed(
                title=":x: Error!",
                description="There was an error loading that track.",
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed)
            return
        elif results.load_type == LoadType.PLAYLIST:
            tracks = results.tracks

            for track in tracks:
                track.extra["requester"] = interaction.user.id
                player.add(track=track)

            embed = discord.Embed(
                title=":play_pause: Playlist Enqueued!",
                description=f"{results.playlist_info.name} - {len(tracks)} track{'s' if len(tracks) > 1 else ''}",
                color=0x00FF00,
            )

            if tracks and tracks[0].artwork_url:
                embed.set_thumbnail(url=tracks[0].artwork_url)
        else:
            track = results.tracks[0]
            track.extra["requester"] = interaction.user.id

            track_length_seconds = track.duration / 1000
            track_minutes = track_length_seconds // 60
            track_seconds = track_length_seconds % 60
            track_length = f"{track_minutes:02.0f}:{track_seconds:02.0f}"

            if not player.is_playing:
                embed = discord.Embed(
                    title=":play_pause: Playing",
                    description=f"{track.author} - {track.title}\n{track_length}",
                    color=0x00FF00,
                )
            else:
                embed = discord.Embed(
                    title=":play_pause: Queued",
                    description=f"{track.author} - {track.title}\n{track_length}",
                    color=0x00FF00,
                )

                queue_position = len(player.queue) + 1
                if queue_position > 1:
                    embed.set_footer(
                        text=f"Use `/skip {queue_position}` to play it directly"
                    )
                else:
                    embed.set_footer(text="Use `/skip` to play it directly")

            if track.artwork_url:
                embed.set_thumbnail(url=track.artwork_url)

            player.add(track=track)

        await interaction.followup.send(embed=embed)

        if not player.is_playing:
            await player.play()

    @app_commands.command(name="skip", description="Skips the current track")
    @app_commands.describe(amount="The number of tracks to skip")
    async def skip(self, interaction: discord.Interaction, amount: int = 1):
        player = await self.ensure_voice(interaction, should_connect=False)
        if player is None:
            return

        if not player.is_playing:
            embed = discord.Embed(
                title=":x: Error!",
                description="Nothing is playing right now.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed)
            return

        # Skip the specified number of tracks
        for i in range(amount - 1):
            if player.queue:
                player.queue.pop(0)

        await player.skip()

        embed = discord.Embed(
            title=":fast_forward: Skipped",
            description=f"Skipped {amount} track{'s' if amount > 1 else ''}",
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue", description="Shows the queue")
    async def queue(self, interaction: discord.Interaction):
        if not await self._check_is_in_guild(interaction):
            return

        assert interaction.guild is not None

        player = self.bot.lavalink.player_manager.get(interaction.guild.id)

        if not player or not player.queue:
            embed = discord.Embed(
                title=":notes: Queue", description="The queue is empty!", color=0x00FF00
            )

            if player and player.current:
                embed.add_field(
                    name="**Now Playing**",
                    value=f"{player.current.author} - {player.current.title}",
                    inline=False,
                )

            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(title=":notes: Queue", color=0x00FF00)

        if player.current:
            embed.add_field(
                name="**Now Playing**",
                value=f"{player.current.author} - {player.current.title}",
                inline=False,
            )

        for i, track in enumerate(player.queue[:10], start=1):
            embed.add_field(
                name=f"**{i}. {track.title}**", value=track.author, inline=False
            )

        if len(player.queue) > 10:
            embed.set_footer(text=f"And {len(player.queue) - 10} more...")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leave", description="Leaves the voice channel")
    async def leave(self, interaction: discord.Interaction):
        if not await self._check_is_in_guild(interaction):
            return

        assert interaction.guild is not None

        player = self.bot.lavalink.player_manager.get(interaction.guild.id)

        if not interaction.guild.voice_client:
            embed = discord.Embed(
                title=":x: Error!",
                description="I'm not in a voice channel.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed)
            return

        await interaction.response.defer()

        player.queue.clear()
        await player.stop()
        await interaction.guild.voice_client.disconnect(force=True)

        embed = discord.Embed(
            title=":wave: Goodbye!",
            description="The bot has left the voice channel.",
            color=0x00FF00,
        )
        await interaction.followup.send(embed=embed)
