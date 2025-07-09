# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import discord
import re
from discord.ext import commands
from app.keys import KeyManager
from app.utils import print_flush


PICS_CHANNEL_ID = KeyManager().get("PICS_CHANNEL_ID")


def isAttachmentMessage(message):
    text = message.content.strip()
    match = re.search(r"https?://\S+", text)
    if not match:
        return False

    url = match.group(0)

    if url.lower().endswith(".gif"):
        return False

    blockedDomains = [
        "giphy.com",
        "tenor.com",
        "imgur.com",
        "reddit.com",
        "i.redd.it",
        "media.giphy.com",
        "media.tenor.com",
        "gfycat.com"
    ]

    for domain in blockedDomains:
        if domain in url.lower():
            return False

    return True


class PicsCleaner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def getThreadName(self, threadCreationMessage: discord.Message, guild: discord.Guild):
        hasPhoto = list(a.content_type and a.content_type.startswith("image/") for a in threadCreationMessage.attachments)
        hasVideo = list(a.content_type and a.content_type.startswith("video/") for a in threadCreationMessage.attachments)
    
        messageContentWithoutLinks = ""
        if threadCreationMessage.content:
            messageContent = threadCreationMessage.content.replace("\n", " ")
            for user in threadCreationMessage.mentions:
                messageContent = messageContent.replace(f"<@{user.id}>", f"{user.display_name}")
                messageContent = messageContent.replace(f"<@!{user.id}>", f"{user.display_name}")

            for word in messageContent.split():
                if word.startswith("http://") or word.startswith("https://"):
                    continue

                if word.startswith("<#") and word.endswith(">"):
                    try:
                        channel = guild.get_channel(int(word[2:-1]))
                        if channel:
                            messageContentWithoutLinks += f"#{channel.name} "
                        else:
                            messageContentWithoutLinks += word + " "
                    except Exception: pass
                    continue

                messageContentWithoutLinks += word + " "

        nickname = threadCreationMessage.author.display_name.strip()
        nickname = re.sub(r"\s*[\(\[\{].*?[\)\]\}]", "", nickname)

        if messageContentWithoutLinks:
            messageContent = messageContentWithoutLinks[:64].strip()
        elif any(hasPhoto):
            messageContent = f"{nickname}'s photo" + ("s" if sum(hasPhoto) > 1 else "")
        elif any(hasVideo):
            messageContent = f"{nickname}'s video" + ("s" if sum(hasVideo) > 1 else "")
        else:
            messageContent = f"Thread for {nickname}'s message"
        
        return messageContent[:100].strip()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or str(message.channel.id) != str(PICS_CHANNEL_ID):
            return

        if message.type in (discord.MessageType.thread_created, discord.MessageType.pins_add):
            await message.delete(delay=900)
            return

        if message.attachments or isAttachmentMessage(message) or message.content.strip() == "":
            return

        parentChannel = message.channel
        if message.reference and message.reference.resolved:
            lastMessageWithImg = message.reference.resolved
        else:
            lastMessageWithImg = None
            async for msg in parentChannel.history(limit=100):
                if msg.id == message.id:
                    continue
                if msg.attachments or isAttachmentMessage(msg):
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
            threadName = self.getThreadName(lastMessageWithImg, message.guild)
            thread = await lastMessageWithImg.create_thread(name=threadName)

        await thread.join()

        await thread.send("<@" + str(message.author.id) + ">")
        
        webhooks = await parentChannel.webhooks()
        webhook = discord.utils.get(webhooks, name="Goober")
        if not webhook:
            try:
                webhook = await parentChannel.create_webhook(name="Goober")
            except discord.Forbidden:
                print_flush("Missing permission to create webhook")
                return

        try:
            await webhook.send(
                content=f"{message.content}",
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url,
                thread=thread
            )
        except discord.HTTPException as e:
            print_flush(f"Failed to send webhook message: {e}")

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        if not thread.parent or str(thread.parent.id) != str(PICS_CHANNEL_ID):
            return

        if thread.name.strip().lower() != "thread":
            return

        try:
            originalMessage = await thread.parent.fetch_message(thread.id)
        except (discord.NotFound, discord.HTTPException):
            return

        threadName = self.getThreadName(originalMessage, thread.guild)

        try:
            await thread.edit(name=threadName)
        except discord.Forbidden:
            print_flush("Missing permissions to rename the thread.")
        
    async def setup(self, bot):
        await bot.add_cog(self)
