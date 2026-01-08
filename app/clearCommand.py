# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import discord
from discord.ext import commands
from datetime import datetime, timedelta
from app.keys import KeyManager
import asyncio


NSFW_CHANNEL_ID = int(KeyManager().get("NSFW_CHANNEL_ID", "0"))

class ClearCommand(commands.Cog):
    bot: discord.Client

    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def setup(self, bot):
        await bot.add_cog(self)

    @commands.command(name="clear")
    async def clear(self, ctx: commands.Context):
        if ctx.channel.id != NSFW_CHANNEL_ID:
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



        last_week = datetime.now() - timedelta(days=3)
        messages = ctx.channel.history(
            before=last_week,
            oldest_first=True,
        )

        await reply.edit(content="Starting to delete messages")
        print(f"Clearing messages from channel #{ctx.channel.id}")
        async for message in messages:
            try:
                await message.delete()
                await asyncio.sleep(1)
            except Exception as e:
                print(e)
                pass

        await reply.edit(content="Deletion Complete")

