import logging
import os

import discord
from discord.ext import commands
from openrouter import OpenRouter

WELCOME_CHANNEL = 832962322967822336
API_KEY_ENV = "OPENROUTER_API_KEY"
MODEL = "openai/gpt-5-mini"


class JoinMessage(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        logging.info("[COG] Join Message Loaded!")
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not os.getenv(API_KEY_ENV):
            logging.error(f"{API_KEY_ENV} environment variable not set")
            await self.bot.remove_cog(self.__class__.__name__)
            return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        with OpenRouter(api_key=os.getenv(API_KEY_ENV)) as open_router:
            response = open_router.chat.send(
                messages=[
                    {
                        "content": "You are a helpful assistant that is welcoming new members to our discord server.",
                        "role": "system",
                    },
                    {
                        "content": f"Generate a short welcome message for the {member.name}. Generate the message in german. Make a funny reference or pun to the users name. You can both be nice or roast them. Answer with the message to send to the channel. Do not include any new-lines. When referencing the users name, use `<@{member.id}>` to tag them.",
                        "role": "user",
                    },
                ],
                mode=MODEL,
                stream=False,
            )

        channel = self.bot.get_channel(WELCOME_CHANNEL)

        if channel and isinstance(channel, discord.TextChannel):
            await channel.send(response.output_text)
        else:
            logging.error(f"Welcome channel {WELCOME_CHANNEL} not found")
