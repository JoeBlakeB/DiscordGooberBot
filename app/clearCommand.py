# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import discord
import time
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from app.keys import KeyManager
import asyncio
from app.utils import print_flush


CLEAR_CHANNEL_ID = int(KeyManager().get("CLEAR_CHANNEL_ID", "0"))

class ClearCommand(commands.Cog):
    bot: discord.Client

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.autoClear.start()

    async def setup(self, bot):
        await bot.add_cog(self)

    def cog_unload(self):
        self.autoClear.cancel()

    @commands.command(name="clear")
    async def clear(self, ctx: commands.Context):
        if ctx.channel.id != CLEAR_CHANNEL_ID:
            await ctx.reply("You can't do that in this channel")
            return

        if not isinstance(ctx.author, discord.Member):
            return

        permissions = ctx.channel.permissions_for(ctx.author)
        if not permissions.administrator:
            await ctx.reply("You don't have the permissions")
            return

        reply = await ctx.reply("You are going to clear all messages older than 3 days from this channel?\nTo continue type CONFIRM")

        try:
            message = await self.bot.wait_for(
                "message",
                check=lambda msg:
                    msg.channel.id == ctx.channel.id and
                    msg.author.id == ctx.author.id,
                timeout=60
            )
        except asyncio.TimeoutError:
            await reply.edit(content="Clear Command Timed Out")
            return

        if message.content != "CONFIRM":
            await reply.edit(content="Confirmation Failed")
            return

        await reply.edit(content="Starting to delete messages")
        print_flush(f"Clearing messages from channel #{ctx.channel.id}")
        threshold = datetime.now() - timedelta(days=3)
        messagesDeleted = await self._delete_messages(ctx.channel, threshold)

        await reply.edit(content="Deletion complete, deleted " + str(messagesDeleted) + " messages")

    async def _delete_messages(self, channel, beforeTime: datetime) -> int:
        """Delete messages in `channel` older than `beforeTime`, skipping pinned messages."""
        messages = channel.history(
            before=beforeTime,
            oldest_first=True,
        )

        timeoutAt = time.time() + (60 * 60)
        messagesDeleted = 0

        async for message in messages:
            if time.time() > timeoutAt:
                print_flush("Message deletion timed out")
                break
            try:
                if message.pinned:
                    continue
                await message.delete()
                messagesDeleted += 1
                await asyncio.sleep(1)
            except Exception as e:
                print_flush(e)
                pass
        
        print_flush(f"Deleted {messagesDeleted} messages from #{channel.id}")
        return messagesDeleted

    @tasks.loop(hours=24)
    async def autoClear(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(CLEAR_CHANNEL_ID)
        if channel is None:
            return print_flush("Error: auto clear channel not found")

        threshold = datetime.now() - timedelta(days=30)
        print_flush(f"Auto-clearing messages in #{channel.id}")
        await self._delete_messages(channel, threshold)

