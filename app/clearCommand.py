# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import ast
import discord
import time
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from app.keys import KeyManager
import asyncio
from app.utils import print_flush

CLEAR_CHANNEL_IDS = KeyManager().get("CLEAR_CHANNEL_IDS", "{}")
if isinstance(CLEAR_CHANNEL_IDS, str):
    try:
        CLEAR_CHANNEL_IDS = ast.literal_eval(CLEAR_CHANNEL_IDS)
    except Exception:
        CLEAR_CHANNEL_IDS = {}
if not isinstance(CLEAR_CHANNEL_IDS, dict):
    CLEAR_CHANNEL_IDS = {}

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
        days = CLEAR_CHANNEL_IDS.get(str(ctx.channel.id)) or CLEAR_CHANNEL_IDS.get(ctx.channel.id)
        if days is None:
            await ctx.reply("You can't do that in this channel")
            return

        if not isinstance(ctx.author, discord.Member):
            return

        permissions = ctx.channel.permissions_for(ctx.author)
        if not permissions.administrator:
            await ctx.reply("You don't have the permissions")
            return


        reply = await ctx.reply(f"You are going to clear ALL messages from this channel.\nTo continue type CONFIRM")

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

        messagesDeleted = await self._delete_all_messages(ctx.channel)

        await reply.edit(content="Deletion complete, deleted " + str(messagesDeleted) + " messages")

    async def _delete_all_messages(self, channel) -> int:
        """Delete all messages in `channel`, skipping pinned messages."""
        messages = channel.history(oldest_first=True)
        timeoutAt = time.time() + (60 * 15)
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

    async def _delete_messages(self, channel, beforeTime: datetime) -> int:
        """Delete messages in `channel` older than `beforeTime`, skipping pinned messages."""
        messages = channel.history(
            before=beforeTime,
            oldest_first=True,
        )

        timeoutAt = time.time() + (60 * 15)
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

    @tasks.loop(minutes=20)
    async def autoClear(self):
        await self.bot.wait_until_ready()
        for channel_id, days in CLEAR_CHANNEL_IDS.items():
            try:
                cid = int(channel_id)
            except Exception:
                continue
            channel = self.bot.get_channel(cid)
            if channel is None:
                print_flush(f"Error: auto clear channel {cid} not found")
                continue
            threshold = datetime.now() - timedelta(days=int(days))
            print_flush(f"Auto-clearing messages in #{cid} older than {days} days")
            await self._delete_messages(channel, threshold)

