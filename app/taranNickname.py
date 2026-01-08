import discord
import re
import time
from discord.ext import commands, tasks
from app.keys import KeyManager
from app.utils import print_flush

TAREN_USER_ID = int(KeyManager().get("TAREN_USER_ID"))

MISSPELLING_REGEX = r"\bT[a-zA-Z]{3,}\b"
EXCLUDED_NAMES = {
    "this", "that", "there", "these", "those", "then", "though", "they", "them", "theirs", "thats", "than", "true",
    "thanks", "thank", "today", "tomorrow", "tonight", "tuesday",
    "time", "told", "tell", "takes", "taking", "tried", "trying",
    "turns", "turned", "turn", "talk", "talked", "talking", "thing",
    "things", "too", "took", "through", "threw", "to", "the",
    "taylor", "tiktok", "twitter", "twitch", "tumblr", 
    "tesla", "toyota", "texas", "turkey", "thailand",
    "tuesday", "thursday", "today", "tomorrow",
    "thread", "tom", "tomura",
}

class TarenNickChanger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.taransNameChangedAt = time.time()
        self.last_message_time = time.time()
        print_flush("TarenNickChanger: Starting reset name loop task...")
        self.reset_name_loop.start()

    def cog_unload(self):
        self.reset_name_loop.cancel()

    def find_misspelling(self, content: str) -> str | None:
        """Return the first detected 'Taran-like' word in the message, if any."""
        if " " in content.strip():
            content = " ".join(content.strip().split(" ")[1:])
        matches = re.findall(MISSPELLING_REGEX, content)
        for word in matches:
            if word.lower() not in EXCLUDED_NAMES:
                return word
        return None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        self.last_message_time = time.time()

        possible_nick = self.find_misspelling(message.content)
        if not possible_nick:
            return

        guild = message.guild
        taran = guild.get_member(TAREN_USER_ID)
        if not taran:
            return

        try:
            if taran.nick.replace(" (Taran)", "").lower() != possible_nick.lower():
                await taran.edit(nick=possible_nick + " (Taran)", reason=f"Auto-nick for '{possible_nick}' found in chat because message from {message.author.name}: {message.content}")
                print_flush(f"Changed Taran's nickname to {possible_nick} because message from {message.author.name}: {message.content}")
                self.taransNameChangedAt = time.time()
        except discord.Forbidden:
            print_flush("Missing permission to change nickname.")
        except Exception as e:
            print_flush(f"Error changing nickname: {e}")

    @tasks.loop(minutes=1)
    async def reset_name_loop(self):
        """Resets Taran's nickname if inactive for 30+ minutes and name changed 4+ hours ago."""
        now = time.time()

        if now - self.last_message_time > 1800 and now - self.taransNameChangedAt > 14400:
            for guild in self.bot.guilds:
                taran = guild.get_member(TAREN_USER_ID)
                if not taran:
                    continue
                if taran.nick != "Taran":
                    try:
                        await taran.edit(nick="Taran", reason="Auto-reset after inactivity and time limit")
                        print_flush("Reset Taran's nickname to 'Taran' due to inactivity.")
                        self.taransNameChangedAt = time.time()
                    except discord.Forbidden:
                        print_flush("Missing permission to reset nickname.")
                    except Exception as e:
                        print_flush(f"Error resetting nickname: {e}")

    @reset_name_loop.before_loop
    async def before_reset_loop(self):
        await self.bot.wait_until_ready()
