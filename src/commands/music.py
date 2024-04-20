import discord
import wavelink
from discord.ext import commands

TESTING_GUILDS = ["902614427541590066", "803587371152441345"]

LAVALINK_HOST = "lavalink4.alfari.id"
LAVALINK_PORT = 443
LAVALINK_PASSWORD = "catfein"

WAVELINK_NODES = [
    wavelink.Node(
        uri=f"https://{LAVALINK_HOST}:{LAVALINK_PORT}",
        password=LAVALINK_PASSWORD,
    )
]


async def wavelink_connect(bot):
    await bot.wait_until_ready()

    pool = wavelink.Pool()

    await pool.connect(nodes=WAVELINK_NODES, client=bot)
    return pool


async def create_player(client, pool, channel):
    node = pool.get_node()

    return wavelink.Player(client=client, channel=channel, nodes=[node])


class Music(commands.Cog):
    def __init__(self, bot):
        print("[COG] Music Cog Loaded!")
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.player = None
        self.wavelink_pool = await wavelink_connect(self.bot)
        print("Launched Wavelink!")

    @commands.slash_command(
        name="join",
        description="Joins your voice channel",
        guild_ids=TESTING_GUILDS,
    )
    async def join(self, ctx):
        author_voice = ctx.author.voice
        author_voice_channel = author_voice.channel

        self.player = await create_player(
            client=self.bot,
            pool=self.wavelink_pool,
            channel=author_voice_channel,
        )

        if not author_voice:
            embed = discord.Embed(
                title=":x: Error!",
                description="You are not in a voice channel",
                color=0xFF0000,
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title=":white_check_mark: Success!",
                description=f"Joined {author_voice_channel.name}",
                color=0x00FF00,
            )

            await author_voice_channel.connect(cls=self.player)

            await ctx.respond(embed=embed)

    @commands.slash_command(
        name="play", description="Plays a song", guild_ids=TESTING_GUILDS
    )
    async def play(self, ctx, search: str):
        author_voice_channel = ctx.author.voice.channel

        if not self.player:
            self.player = await create_player(
                client=self.bot,
                pool=self.wavelink_pool,
                channel=author_voice_channel,
            )

        if not self.player.connected:
            await author_voice_channel.connect(cls=self.player)
            print(f"Connected: {author_voice_channel}")

        print(f"Connected: {self.player.connected}")

        print(f"Searching: {search}")
        tracks = await wavelink.Playable.search(search)

        print(f"Tracks: {tracks}")

        top_track = tracks[0]

        track_length_seconds = top_track.length / 1000
        track_minutes = track_length_seconds // 60
        track_seconds = track_length_seconds % 60
        track_length = f"{track_minutes:02.0f}:{track_seconds:02.0f}"

        embed = discord.Embed(
            title=":play_pause: Playing",
            description=f"""
                {top_track.author} - {top_track.title}
                {track_length}
            """,
            color=0x00FF00,
        )

        embed.set_thumbnail(url=top_track.artwork)

        await ctx.respond(embed=embed)

        print(f"Playing: {top_track.title}")
        await self.player.play(top_track)

    @commands.slash_command(
        text="leave",
        description="Leaves the voice channel",
        guild_ids=TESTING_GUILDS,
    )
    async def leave(self, ctx):
        await self.player.stop()
        await self.player.disconnect()
        self.player = None

        embed = discord.Embed(
            title=":wave: Goodbye!",
            description="The bot has left the voice channel.",
            color=0x00FF00,
        )

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))
