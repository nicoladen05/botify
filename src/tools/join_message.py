import logging
import os

import discord
from discord.ext import commands
from openai import OpenAI

WELCOME_CHANNEL = 832962322967822336


class JoinMessage(commands.Cog):
    openai_client: OpenAI
    bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        logging.info("[COG] Join Message Loaded!")
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not (openai_api_key := os.getenv("OPENAI_API_KEY")):
            logging.error("OPENAI_API_KEY environment variable not set")
            await self.bot.remove_cog(self.__class__.__name__)

        self.openai_client = OpenAI(api_key=openai_api_key)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        response = self.openai_client.responses.create(
            model="gpt-5-mini",
            instructions="You are a helpful assistant that is welcoming new members to our discord server.",
            input=f"Generate a short welcome message for the {member.name}. Generate the message in german. Make a funny reference or pun to the users name. You can both be nice or roast them. Answer with the message to send to the channel. Do not include any new-lines. When referencing the users name, use `<@{member.id}>` to tag them.",
        )

        channel = self.bot.get_channel(WELCOME_CHANNEL)

        if channel and isinstance(channel, discord.TextChannel):
            await channel.send(response.output_text)
        else:
            logging.error(f"Welcome channel {WELCOME_CHANNEL} not found")
