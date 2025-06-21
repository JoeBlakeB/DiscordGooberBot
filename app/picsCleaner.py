# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import discord
from discord.ext import commands
from app.keys import KeyManager


PICS_CHANNEL_ID = KeyManager().get("PICS_CHANNEL_ID")


class PicsCleaner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.channel.id != PICS_CHANNEL_ID:
            return

        if message.attachments:
            return

        parentChannel = message.channel
        lastMessageWithImg = None
        async for msg in parentChannel.history(limit=100):
            if msg.id == message.id:
                continue
            if msg.attachments:
                lastMessageWithImg = msg
                break

        if not lastMessageWithImg: return

        try:
            await message.delete()
        except discord.Forbidden:
            return

        thread = None
        if lastMessageWithImg.thread:
            thread = lastMessageWithImg.thread
        else:
            hasPhoto = any(a.content_type and a.content_type.startswith("image/") for a in lastMessageWithImg.attachments)
            hasVideo = any(a.content_type and a.content_type.startswith("video/") for a in lastMessageWithImg.attachments)

            if lastMessageWithImg.content:
                messageContent = lastMessageWithImg.content[:64]
            elif hasPhoto:
                messageContent = f"{lastMessageWithImg.author.name}'s photo"
            elif hasVideo:
                messageContent = f"{lastMessageWithImg.author.name}'s video"
            else:
                messageContent = f"Thread for {lastMessageWithImg.author.name}'s message"

            thread = await lastMessageWithImg.create_thread(name=messageContent[:800])

        await thread.join()

        await thread.send("<@" + str(message.author.id) + ">")
        
        webhooks = await parentChannel.webhooks()
        webhook = discord.utils.get(webhooks, name="Goober")
        if not webhook:
            try:
                webhook = await parentChannel.create_webhook(name="Goober")
            except discord.Forbidden:
                print("Missing permission to create webhook")
                return

        try:
            await webhook.send(
                content=f"{message.content}",
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url,
                thread=thread
            )
        except discord.HTTPException as e:
            print(f"Failed to send webhook message: {e}")

        
    async def setup(self, bot):
        await bot.add_cog(self)
