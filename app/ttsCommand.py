# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import io
import subprocess as sp
from pathlib import Path
import discord
from tempfile import gettempdir
from discord.ext import commands
import pyttsx4
from contextlib import suppress


engine = pyttsx4.init()

class TTSCommand(commands.Cog):
    bot: discord.Client

    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def setup(self, bot):
        await bot.add_cog(self)

    @commands.command(name="tts")
    async def tts(self, ctx: commands.Context, *, text: str):
        if not isinstance(ctx.author, discord.Member):
            return

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("You have to be in a voice channel to use this command")
            return

        buf = tts(text)

        with suppress(Exception):
            await ctx.author.voice.channel.connect()
            
        audio = discord.FFmpegOpusAudio(buf, pipe=True)
        ctx.voice_client.play(audio)



def tts(text: str) -> io.BytesIO:
    FILENAME = "tts.temp.wav"
    engine.setProperty('voice', "English (Great Britain)")
    engine.setProperty("rate", 140)
    engine.save_to_file(text, FILENAME)
    engine.runAndWait()

    filters = [
        "equalizer=f=300:width_type=h:w=200:g=-5",
        "equalizer=f=4000:width_type=h:w=1000:g=3",
        "compand=0.3|0.8:6:-70/-60|-20/-2|0/-2",
        "highpass=f=200",
        "lowpass=f=2300",
        "rubberband=pitch=1.5"
    ]
    proc = sp.Popen(
        args=[
            "ffmpeg",
            "-i", FILENAME,
            "-f", "wav",
            "-af", ",".join(filters),
            "-"
        ],
        stdout=sp.PIPE,
        stderr=sp.DEVNULL
    )
    return proc.stdout # type: ignore
