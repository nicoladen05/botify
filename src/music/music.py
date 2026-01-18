import asyncio
import logging
from collections import deque
from typing import Any, cast

import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands

INACTIVITY_TIMEOUT = 10 * 60

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}

ffmpeg_options = {
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)  # pyright: ignore[reportArgumentType]


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data: dict[str, Any], volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title: str = data.get("title", "")
        self.url: str = data.get("url", "")
        self.duration: int | None = data.get("duration")
        self.thumbnail: str | None = data.get("thumbnail")
        self.uploader: str | None = data.get("uploader")

    @classmethod
    async def from_url(
        cls,
        url: str,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        stream: bool = False,
    ):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        data = cast(dict[str, Any], data)
        # Cast to Any to satisfy _InfoDict requirement for prepare_filename
        filename = data["url"] if stream else ytdl.prepare_filename(cast(Any, data))
        return cls(
            discord.FFmpegPCMAudio(filename, options=ffmpeg_options["options"]),
            data=data,
        )


class Music(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot
        self.queues: dict[int, deque[str]] = {}  # Guild ID -> deque of YTDLSource info
        self.timeout_tasks: dict[int, asyncio.Task] = {}
        logging.info("[COG] Music Cog Loaded!")

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

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
        if not await self._check_is_in_guild(interaction):
            return None

        assert interaction.guild is not None
        assert isinstance(interaction.user, discord.Member)

        voice_client = interaction.guild.voice_client

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=":x: Error!",
                    description="You need to join a voice channel first.",
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

            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=":x: Error!",
                    description="You need to be in my voice channel.",
                    color=0xFF0000,
                ),
                ephemeral=True,
            )
            return None

        return cast(discord.VoiceClient, voice_client)

    async def disconnect_timer(self, guild_id: int, interaction: discord.Interaction):
        await asyncio.sleep(INACTIVITY_TIMEOUT)  # 10 minutes
        if guild_id in self.timeout_tasks:
            del self.timeout_tasks[guild_id]

        guild = self.bot.get_guild(guild_id)
        if not guild or not guild.voice_client:
            return

        voice_client = guild.voice_client
        if isinstance(voice_client, discord.VoiceClient):
            await voice_client.disconnect(force=True)
            self.queues.pop(guild_id, None)

            embed = discord.Embed(
                title=":zzz: Inactivity",
                description="Left the voice channel due to inactivity.",
                color=0xFFA500,
            )
            # Try to send to the channel where interaction happened, or just log if fails
            try:
                if interaction.channel and isinstance(
                    interaction.channel, discord.abc.Messageable
                ):
                    await interaction.channel.send(embed=embed)
            except Exception:
                pass

    def start_disconnect_timer(self, guild_id: int, interaction: discord.Interaction):
        self.stop_disconnect_timer(guild_id)
        self.timeout_tasks[guild_id] = self.bot.loop.create_task(
            self.disconnect_timer(guild_id, interaction)
        )

    def stop_disconnect_timer(self, guild_id: int):
        if guild_id in self.timeout_tasks:
            self.timeout_tasks[guild_id].cancel()
            del self.timeout_tasks[guild_id]

    def play_next(self, interaction: discord.Interaction):
        if not interaction.guild:
            return

        queue = self.get_queue(interaction.guild.id)
        if len(queue) > 0:
            next_url = queue.popleft()

            # We need to create a task because play_next is a synchronous callback
            asyncio.run_coroutine_threadsafe(
                self.start_playing(interaction, next_url), self.bot.loop
            )
        else:
            # Queue empty, start timer
            self.start_disconnect_timer(interaction.guild.id, interaction)

    async def start_playing(self, interaction: discord.Interaction, search: str):
        if not interaction.guild:
            return
        voice_client = cast(discord.VoiceClient, interaction.guild.voice_client)
        if not voice_client:
            return

        # Stop timer when playing starts
        self.stop_disconnect_timer(interaction.guild.id)

        try:
            player = await YTDLSource.from_url(search, loop=self.bot.loop, stream=True)

            voice_client.play(player, after=lambda e: self.play_next(interaction))

            track_length_seconds = player.duration
            if track_length_seconds:
                track_minutes = track_length_seconds // 60
                track_seconds = track_length_seconds % 60
                track_length = f"{track_minutes:02.0f}:{track_seconds:02.0f}"
            else:
                track_length = "Unknown"

            embed = discord.Embed(
                title=":play_pause: Now Playing",
                description=f"{player.uploader} - {player.title}\n{track_length}",
                color=0x00FF00,
            )
            if player.thumbnail:
                embed.set_thumbnail(url=player.thumbnail)

            try:
                await interaction.followup.send(embed=embed)
            except discord.NotFound:
                if interaction.channel and isinstance(
                    interaction.channel, discord.abc.Messageable
                ):
                    await interaction.channel.send(embed=embed)

        except Exception as e:
            logging.error(f"Error playing track: {e}")
            if interaction.channel and isinstance(
                interaction.channel, discord.abc.Messageable
            ):
                await interaction.channel.send(f"An error occurred: {e}")

            # Restart timer if failed to play and still connected
            if (
                interaction.guild
                and interaction.guild.voice_client
                and not voice_client.is_playing()
            ):
                self.start_disconnect_timer(interaction.guild.id, interaction)

    @app_commands.command(name="join", description="Joins your voice channel")
    async def join(self, interaction: discord.Interaction):
        voice_client = await self.ensure_voice(interaction, should_connect=True)
        if voice_client:
            embed = discord.Embed(
                title=":white_check_mark: Success!",
                description=f"Joined {voice_client.channel.name}",
                color=0x00FF00,
            )
            await interaction.response.send_message(embed=embed)
            # Start timer on join if not playing
            if not voice_client.is_playing() and interaction.guild:
                self.start_disconnect_timer(interaction.guild.id, interaction)

    @app_commands.command(name="play", description="Plays a song")
    @app_commands.describe(search="The song to search for or URL to play")
    async def play(self, interaction: discord.Interaction, search: str):
        voice_client = await self.ensure_voice(interaction, should_connect=True)
        if not voice_client:
            return

        await interaction.response.defer()

        # If already playing, add to queue
        if voice_client.is_playing() or voice_client.is_paused():
            assert interaction.guild
            queue = self.get_queue(interaction.guild.id)
            queue.append(search)  # Store the search term/url

            embed = discord.Embed(
                title=":play_pause: Queued",
                description=f"Added to queue: {search}",
                color=0x00FF00,
            )
            await interaction.followup.send(embed=embed)
        else:
            await self.start_playing(interaction, search)

    @app_commands.command(name="skip", description="Skips the current track")
    async def skip(self, interaction: discord.Interaction):
        if not await self._check_is_in_guild(interaction):
            return

        assert interaction.guild

        voice_client = cast(discord.VoiceClient, interaction.guild.voice_client)
        if not voice_client or not (
            voice_client.is_playing() or voice_client.is_paused()
        ):
            embed = discord.Embed(
                title=":x: Error!",
                description="Nothing is playing right now.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed)
            return

        voice_client.stop()

        embed = discord.Embed(
            title=":fast_forward: Skipped",
            description="Skipped the current track.",
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pause", description="Pauses the current track")
    async def pause(self, interaction: discord.Interaction):
        if not await self._check_is_in_guild(interaction):
            return

        assert interaction.guild
        voice_client = cast(discord.VoiceClient, interaction.guild.voice_client)

        if not voice_client or not voice_client.is_playing():
            embed = discord.Embed(
                title=":x: Error!",
                description="Nothing is playing right now.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed)
            return

        voice_client.pause()
        self.start_disconnect_timer(interaction.guild.id, interaction)

        embed = discord.Embed(
            title=":pause_button: Paused",
            description="Playback paused.",
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="resume", description="Resumes the current track")
    async def resume(self, interaction: discord.Interaction):
        if not await self._check_is_in_guild(interaction):
            return

        assert interaction.guild
        voice_client = cast(discord.VoiceClient, interaction.guild.voice_client)

        if not voice_client or not voice_client.is_paused():
            embed = discord.Embed(
                title=":x: Error!",
                description="The music is not paused.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed)
            return

        voice_client.resume()
        self.stop_disconnect_timer(interaction.guild.id)

        embed = discord.Embed(
            title=":play_pause: Resumed",
            description="Playback resumed.",
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue", description="Shows the queue")
    async def queue(self, interaction: discord.Interaction):
        if not await self._check_is_in_guild(interaction):
            return

        assert interaction.guild

        queue = self.get_queue(interaction.guild.id)
        if not queue:
            embed = discord.Embed(
                title=":notes: Queue", description="The queue is empty!", color=0x00FF00
            )
            await interaction.response.send_message(embed=embed)
            return

        description = "\n".join([f"{i + 1}. {item}" for i, item in enumerate(queue)])
        # Cap description length if needed
        if len(description) > 4000:
            description = description[:4000] + "..."

        embed = discord.Embed(
            title=":notes: Queue", description=description, color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leave", description="Leaves the voice channel")
    async def leave(self, interaction: discord.Interaction):
        if not await self._check_is_in_guild(interaction):
            return

        assert interaction.guild

        voice_client = cast(discord.VoiceClient, interaction.guild.voice_client)
        if not voice_client:
            embed = discord.Embed(
                title=":x: Error!",
                description="I'm not in a voice channel.",
                color=0xFF0000,
            )
            await interaction.response.send_message(embed=embed)
            return

        self.stop_disconnect_timer(interaction.guild.id)
        queue = self.get_queue(interaction.guild.id)
        queue.clear()
        await voice_client.disconnect(force=True)

        embed = discord.Embed(
            title=":wave: Goodbye!",
            description="The bot has left the voice channel.",
            color=0x00FF00,
        )
        await interaction.response.send_message(embed=embed)
