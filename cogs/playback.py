import discord
from discord.ext import commands


class PlaybackCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play")
    async def play(self, ctx):
        async with ctx.channel.typing():
            connected = ctx.author.voice
            if connected:
                vc = await connected.channel.connect()

                source = await discord.FFmpegOpusAudio.from_probe(executable="D:/ffmpeg/bin/ffmpeg.exe",
                                                                  source="assets/audio/coffin_dance.mp3",
                                                                  method="fallback")

                print(source)
                vc.play(source)

    @commands.command(name="stop")
    async def stop(self, ctx):
        async with ctx.channel.typing():
            connected = ctx.author.voice
            if connected:
                await connected.channel.disconnect()


def setup(bot):
    bot.add_cog(PlaybackCog(bot))
