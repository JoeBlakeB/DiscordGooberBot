#!/usr/bin/env python3
# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import asyncio
import argparse
import os


def parseArgs():
    parser = argparse.ArgumentParser(description="Start the bot with the specified options.")

    parser.add_argument("-d", "--data-dir", default=os.path.join(os.path.dirname(__file__), "data"), 
                        help="Set the directory where data is stored (default: data)")
    
    return parser.parse_args()


args = parseArgs()
os.environ["DATA_DIR"] = args.data_dir


import discord
from discord.ext import commands
from app.keys import KeyManager
from app.picsCleaner import PicsCleaner
from app.impersonateCommand import ImpersonateCommand


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True
intents.guild_messages = True

COMMAND_PREFIX = KeyManager().get("COMMAND_PREFIX", "!")
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

DISCORD_BOT_TOKEN = KeyManager().get("DISCORD_BOT_TOKEN")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    else:
        raise error


async def addCogs(bot):
    for extension in [
        PicsCleaner(bot),
        ImpersonateCommand(bot),
    ]:
        await bot.add_cog(extension)


if __name__ == "__main__":
    KeyManager().reportMissingKeys()

    asyncio.run(addCogs(bot))
    bot.run(DISCORD_BOT_TOKEN, reconnect=True)
    
