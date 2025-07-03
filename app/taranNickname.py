# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import discord
import re
from discord.ext import commands
from app.keys import KeyManager

TAREN_USER_ID = int(KeyManager().get("TAREN_USER_ID"))

MISSPELLING_REGEX = r"\bT[a-z]{3,}\b"
EXCLUDED_NAMES = {
    "This", "That", "There", "These", "Those", "Then", "Though",
    "Thanks", "Thank", "Today", "Tomorrow", "Tonight", "Tuesday",
    "Time", "Told", "Tell", "Takes", "Taking", "Tried", "Trying",
    "Turns", "Turned", "Turn", "Talk", "Talked", "Talking", "Thing",
    "Things", "Too", "Took", "Through", "Threw", "To", "The",
    "Taylor", "TikTok", "Twitter", "Twitch", "Tumblr", 
    "Tesla", "Toyota", "Texas", "Turkey", "Thailand",
    "Tuesday", "Thursday", "Today", "Tomorrow",
    "Thread",
}

class TarenNickChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def find_misspelling(self, content: str) -> str | None:
        """Return the first detected 'Taren-like' word in the message, if any."""
        matches = re.findall(MISSPELLING_REGEX, content)
        for word in matches:
            if word not in EXCLUDED_NAMES:
                return word
        return None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        possible_nick = self.find_misspelling(message.content)
        if not possible_nick:
            return

        guild = message.guild
        taren = guild.get_member(TAREN_USER_ID)
        if not taren:
            return

        try:
            if taren.nick != possible_nick:
                await taren.edit(nick=possible_nick, reason=f"Auto-nick for '{possible_nick}' found in chat")
                print(f"Changed Taren's nickname to {possible_nick} because message from {message.author.name}: {message.content}")
        except discord.Forbidden:
            print("Missing permission to change nickname.")
        except Exception as e:
            print(f"Error changing nickname: {e}")

    async def setup(self, bot):
        await bot.add_cog(self)
