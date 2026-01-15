import logging

import discord
import lavalink
from discord.ext import commands


class MusicPlayer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        assert bot.user is not None

        logging.info("[COG] Music Cog Loaded!")
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self): ...

    @discord.app_commands.command(
        name="join",
        description="Joins your voice channel",
    )
    async def join(self, interaction: discord.Interaction):
        if isinstance(interaction.user, discord.User):
            embed = discord.Embed(
                title=":x: Error!",
                description="This command only works in servers!",
                color=0xFF0000,
            )
            return await interaction.response.send_message(embed=embed)

        if interaction.user.voice and interaction.user.voice.channel:
            embed = discord.Embed(
                title=":white_check_mark: Success!",
                description=f"Joined {interaction.user.voice.channel.name}",
                color=0x00FF00,
            )
            await interaction.user.voice.channel.connect()

            return await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title=":x: Error!",
                description="You are not in a voice channel",
                color=0xFF0000,
            )
            return await interaction.response.send_message(embed=embed)


#     @commands.slash_command(
#         name="play", description="Plays a song", guild_ids=TESTING_GUILDS
#     )
#     async def play(self, ctx, search: str):
#         author_voice_channel = ctx.author.voice.channel

#         if not self.player:
#             self.player = await create_player(
#                 client=self.bot,
#                 pool=self.wavelink_pool,
#                 channel=author_voice_channel,
#                 queue=self.queue,
#             )

#         if not self.player.connected:
#             await author_voice_channel.connect(cls=self.player)
#             print(f"Connected: {author_voice_channel}")

#         print(f"Connected: {self.player.connected}")

#         print(f"Searching: {search}")
#         tracks = await wavelink.Playable.search(search)

#         print(f"Tracks: {tracks}")

#         top_track = tracks[0]
#         playlist = top_track.playlist

#         if not playlist:
#             track_length_seconds = top_track.length / 1000
#             track_minutes = track_length_seconds // 60
#             track_seconds = track_length_seconds % 60
#             track_length = f"{track_minutes:02.0f}:{track_seconds:02.0f}"

#             author = top_track.author
#             title = top_track.title
#             secondary_info = track_length
#             artwork = top_track.artwork

#             print(f"Queueing: {top_track.title}")
#             self.queue.put(top_track)
#         else:
#             author = playlist.author
#             title = playlist.name
#             secondary_info = (
#                 f"{playlist.tracks} track{'s' if playlist.tracks > 1 else ''}"
#             )
#             artwork = playlist.artwork

#             self.queue.put(tracks)

#         if not self.player.playing:
#             queued_track = self.queue.get()
#             await self.player.play(queued_track)

#             embed = discord.Embed(
#                 title=f":play_pause: Playing{' playlist' if playlist else ''}",
#                 description=f"""
#                     {author} - {title}
#                     {secondary_info}
#                 """,
#                 color=0x00FF00,
#             )

#             embed.set_thumbnail(url=artwork)
#         else:
#             if self.queue.count > 1:
#                 skip_argument = " " + str(self.queue.count)
#             else:
#                 skip_argument = ""

#             embed = discord.Embed(
#                 title=":play_pause: Queued",
#                 description=f"""
#                     {top_track.author} - {top_track.title}
#                     {track_length}
#                 """,
#                 color=0x00FF00,
#             )

#             embed.set_footer(text=f"Use `/skip{skip_argument}` to play it directly")

#             embed.set_thumbnail(url=top_track.artwork)

#         await ctx.respond(embed=embed)

#     @commands.slash_command(
#         text="skip",
#         description="Skips the current track",
#         guild_ids=TESTING_GUILDS,
#     )
#     async def skip(
#         self,
#         ctx,
#         ammount: Option(
#             int, "The ammount of tracks to skip", required=False, default=1
#         ),
#     ):
#         for i in range(ammount):
#             await self.player.skip()

#         embed = discord.Embed(
#             title=":fast_forward: Skipped",
#             description=f"""
#                     Skipped {ammount} track{("s" if ammount > 1 else "")}
#                     """,
#             color=0x00FF00,
#         )

#         await ctx.respond(embed=embed)

#     @commands.slash_command(
#         text="queue",
#         description="Shows the queue",
#         guild_ids=TESTING_GUILDS,
#     )
#     async def queue(self, ctx):
#         embed = discord.Embed(
#             title=":notes: Queue",
#             color=0x00FF00,
#         )

#         if not self.queue:
#             embed.description = "The queue is empty!"

#         for song in self.queue:
#             embed.add_field(name=f"**{song.title}**", value=song.author, inline=False)

#         await ctx.respond(embed=embed)

#     @commands.slash_command(
#         text="leave",
#         description="Leaves the voice channel",
#         guild_ids=TESTING_GUILDS,
#     )
#     async def leave(self, ctx):
#         await self.player.stop()
#         await self.player.disconnect()
#         self.player = None

#         embed = discord.Embed(
#             title=":wave: Goodbye!",
#             description="The bot has left the voice channel.",
#             color=0x00FF00,
#         )

#         await ctx.respond(embed=embed)


# def setup(bot):
#     bot.add_cog(Music(bot))
