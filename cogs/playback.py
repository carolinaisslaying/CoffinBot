import discord
import wavelink
import aiohttp
from io import BytesIO
from discord.ext import commands


class InvokedChannels(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


class Playback(commands.Cog, wavelink.WavelinkMixin):

    def __init__(self, bot):
        self.bot = bot
        self.channels = InvokedChannels()

        if not hasattr(bot, "wavelink"):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())

    @wavelink.WavelinkMixin.listener("on_track_end")
    async def on_track_end(self, node: wavelink.Node, payload):
        tracks = await self.bot.wavelink.get_tracks(self.bot.settings["coffinVideoURL"])

        if not tracks:
            tracks = await self.bot.wavelink.get_tracks(self.bot.settings["coffinVideoURL"])
            if not tracks:
                ctx = self.bot.get_channel(self.channels.get(payload.player.guild_id))
                await ctx.send(f"{self.bot.settings['formats']['error']} **YT Ratelimited:** I am unable to "
                               f"play this video as I am currently ratelimited by YouTube, please try "
                               f"again later.")
                return self.channels.pop(ctx.guild.id)

        await payload.player.play(tracks[0])

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        await self.bot.wavelink.initiate_node(host=self.bot.settings["lavalink"]["host"],
                                              port=self.bot.settings["lavalink"]["port"],
                                              rest_uri=f"http://{self.bot.settings['lavalink']['host']}:"
                                                       f"{self.bot.settings['lavalink']['port']}",
                                              password=self.bot.settings["lavalink"]["password"],
                                              identifier=self.bot.settings["lavalink"]["identifier"],
                                              region=self.bot.settings["lavalink"]["region"])

    async def connect(self, channel: discord.VoiceChannel, guild: discord.Guild):
        player = self.bot.wavelink.get_player(guild.id)
        await player.connect(channel.id)

    @commands.command(name="play", description="Joins the bot to your channel and play's coffin dance.")
    async def play(self, ctx):
        async with ctx.channel.typing():
            if ctx.author.voice is None:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Not connected:** You must be "
                                      f"connected to a voice channel to run this command.")

            join_channel = ctx.guild.get_channel(ctx.author.voice.channel.id)
            if join_channel.permissions_for(ctx.guild.me).connect is False:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Permissions error:** I do not have "
                                      f"the required permission(s) to join the channel you are currently in.")

            if join_channel.permissions_for(ctx.guild.me).speak is False:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Permissions error:** I do not have "
                                      f"the required permission(s) to speak in the channel you are currently in.")

            player = self.bot.wavelink.get_player(ctx.guild.id)
            if player.is_connected:
                return await ctx.send(f"{self.bot.settings['formats']['error']} **Already connected:** I am already "
                                      f"connected to a voice channel on this server.")

            async with aiohttp.ClientSession() as session:
                async with session.get(self.bot.settings["coffinDanceGifURL"]) as resp:
                    buffer = BytesIO(await resp.read())

            tracks = await self.bot.wavelink.get_tracks(self.bot.settings["coffinVideoURL"])

            if not tracks:
                tracks = await self.bot.wavelink.get_tracks(self.bot.settings["coffinVideoURL"])
                if not tracks:
                    return await ctx.send(f"{self.bot.settings['formats']['error']} **YT Ratelimited:** I am unable to "
                                          f"play this video as I am currently ratelimited by YouTube, please try "
                                          f"again later.")

            player = self.bot.wavelink.get_player(ctx.guild.id)
            if not player.is_connected:
                await self.connect(ctx.author.voice.channel, ctx.guild)

            await ctx.send(file=discord.File(fp=buffer, filename="coffin.gif"))
            self.channels.add(ctx.guild.id, ctx.channel.id)
            await player.play(tracks[0])

    @commands.command(name="stop", description="Stops the bot from playing audio and makes it leave the channel.")
    async def stop(self, ctx):
        async with ctx.channel.typing():
            player = self.bot.wavelink.get_player(ctx.guild.id)

            if player.is_connected:
                if player.channel_id != ctx.author.voice.channel.id:
                    return await ctx.send(f"{self.bot.settings['formats']['error']} **Channel error:** You must be in "
                                          f"the same channel as the bot to execute this command.")

                await player.destroy()
                self.channels.pop(ctx.guild.id)
                await ctx.send(f"{self.bot.settings['formats']['success']} **Stopped playing:** I have stopped playing "
                               f"and left the channel.")
            else:
                await ctx.send(f"{self.bot.settings['formats']['error']} **Not playing:** I am currently not playing "
                               f"anything in this server, therefore I cannot 'stop'.")


def setup(bot):
    bot.add_cog(Playback(bot))
