import logging
import os

import discord
from discord.ext import commands
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

WELCOME_CHANNEL = 832962322967822336


class JoinMessage(commands.Cog):
    openai_client: OpenAI | None
    bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        logging.info("[COG] Join Message Loaded!")
        self.bot = bot
        self.openai_client = None

    @commands.Cog.listener()
    async def on_ready(self):
        if not (openai_api_key := os.getenv("OPENAI_API_KEY")):
            logging.error("OPENAI_API_KEY environment variable not set")
            _ = await self.bot.remove_cog(self.__class__.__name__)
            return

        self.openai_client = OpenAI(api_key=openai_api_key)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            if not self.openai_client:
                logging.error("[JOIN_MESSAGE] OpenAI client not initialized")
                return

            messages: list[ChatCompletionMessageParam] = [
                {
                    "role": "system",
                    "content": """# Identity
You are a friendly Discord welcome bot that generates personalized German welcome messages.

# Instructions
- Generate short, humorous welcome messages in German
- Make a funny pun or reference to the user's name
- Be either nice or playfully roast them
- Use the provided user mention format to tag them
- Keep messages to 1-2 sentences maximum
- Do not include newlines in your response

# Examples
<user_name>Max</user_name>
<assistant_response>Willkommen <@123456789>! Hoffe du bist nicht so "maximal" wie dein Name klingt! 🎮</assistant_response>

<user_name>Sarah</user_name>
<assistant_response>Hey <@987654321>! "Sarah" klingt nach "Sahara" - hoffe du bist nicht so trocken! 😄</assistant_response>""",
                },
                {
                    "role": "user",
                    "content": f"Generate a welcome message for {member.name} using <@{member.id}> to tag them.",
                },
            ]

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini", messages=messages, max_tokens=100, temperature=0.8
            )

            welcome_message = response.choices[0].message.content

            channel = self.bot.get_channel(WELCOME_CHANNEL)

            if channel and isinstance(channel, discord.TextChannel):
                _ = await channel.send(welcome_message)
            else:
                logging.error(f"Welcome channel {WELCOME_CHANNEL} not found")

        except Exception as e:
            logging.error(f"[JOIN_MESSAGE] Failed to generate welcome message: {e}")
            fallback_message = f"Willkommen auf dem Server, <@{member.id}>! 🎉"

            channel = self.bot.get_channel(WELCOME_CHANNEL)
            if channel and isinstance(channel, discord.TextChannel):
                _ = await channel.send(fallback_message)
