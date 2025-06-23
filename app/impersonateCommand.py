# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import discord
from discord.ext import commands


class ImpersonateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="impersonate")
    async def impersonate(self, ctx: commands.Context, user: discord.Member, *, message: str):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        targetChannel = ctx.channel
        webhookChannel = ctx.channel.parent if isinstance(ctx.channel, discord.Thread) else ctx.channel

        webhooks = await webhookChannel.webhooks()
        webhook = discord.utils.get(webhooks, name="Goober")
        if not webhook:
            try:
                webhook = await webhookChannel.create_webhook(name="Goober")
            except discord.Forbidden:
                return print(f"Failed to create webhook in channel {webhookChannel.id}. Check permissions.")

        print(f"{ctx.author} impersonated {user} in {targetChannel} with message: {message}")

        try:
            await webhook.send(
                content=message,
                username=user.display_name,
                avatar_url=user.display_avatar.url,
                **({"thread": targetChannel} if isinstance(targetChannel, discord.Thread) else {})
            )
        except discord.HTTPException as e:
            print(f"Failed to send webhook message: {e}")

    async def setup(self, bot):
        await bot.add_cog(self)
