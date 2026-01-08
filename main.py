#!/usr/bin/env python3
# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import asyncio
import argparse
import os


def parseArgs():
    parser = argparse.ArgumentParser(description="Start the bot with the specified options.")

    parser.add_argument(
        "-d", "--data-dir",
        default=os.path.join(os.path.dirname(__file__), "data"),
        help="Set the directory where data is stored (default: data)"
    )

    return parser.parse_args()


args = parseArgs()
os.environ["DATA_DIR"] = args.data_dir


import discord
from discord.ext import commands
from app.keys import KeyManager
from app.picsCleaner import PicsCleaner
from app.impersonateCommand import ImpersonateCommand
from app.taranNickname import TarenNickChanger
from app.ttsCommand import TTSCommand
from app.clearCommand import ClearCommand


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
    cogs = [
        PicsCleaner(bot),
        ImpersonateCommand(bot),
        TarenNickChanger(bot),
        ClearCommand(bot),
        TTSCommand(bot),
    ]
    for cog in cogs:
        await bot.add_cog(cog)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


async def setup_hook():
    await addCogs(bot)
bot.setup_hook = setup_hook


if __name__ == "__main__":
    KeyManager().reportMissingKeys()

    bot.run(DISCORD_BOT_TOKEN, reconnect=True)

