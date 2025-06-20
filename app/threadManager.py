# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import discord
import datetime
from discord.ext import commands
from app.keys import KeyManager


PICS_CHANNEL_ID = KeyManager().get("PICS_CHANNEL_ID")


class ThreadManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        if thread.archived:
            return

        if thread.parent_id != PICS_CHANNEL_ID:
            return

        await thread.join()

        guild = thread.guild
        if not guild:
            return
        
        parentChannel = thread.parent
        viewableMembers = [m for m in guild.members if parentChannel.permissions_for(m).read_messages]

        for member in viewableMembers:
            try:
                await thread.add_user(member)
                await discord.utils.sleep_until(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=0.2))
            except discord.Forbidden:
                print(f"No permission to add {member}")
            except discord.HTTPException:
                print(f"Rate limit or HTTP error while adding {member}")
        
    async def setup(self, bot):
        await bot.add_cog(self)
