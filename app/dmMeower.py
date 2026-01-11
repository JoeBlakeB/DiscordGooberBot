# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import discord
import random
from discord.ext import commands

MEOWS = [
    "meow",
    "nya",
    "mew",
    "miau",
    "meowww",
    "meaow",
    "mrow",
    "prr",
    "meow~",
]

FACES = [
    *[":3"] * 5,
    *[";3"] * 3,
    ">:3",
    ">;3",
    "UwU",
    ">w<",
    "^w^",
]

def randomMeow():
    if random.randint(1,3) == 1:
        meow = random.choice(MEOWS[:-1]) + " " + random.choice(MEOWS)
        faceChance = 5
    else:
        meow = random.choice(MEOWS)
        faceChance = 2

    if random.randint(1,faceChance) == 1:
        meow += " " + random.choice(FACES)

    return meow

class DmMeower(commands.Cog):
    bot: discord.Client

    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def setup(self, bot):
        await bot.add_cog(self)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None and not message.author.bot:
            await message.channel.send(randomMeow())
