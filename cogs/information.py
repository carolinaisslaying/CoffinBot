import discord
import wavelink
import aiohttp
from io import BytesIO
from discord.ext import commands


class Information(commands.Cog, wavelink.WavelinkMixin):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="privacy", description="Provides you with the bot's Privacy Policy (required as per Discord Developer ToS).")
    async def privacy(self, ctx):
        if not ctx.guild:
            colour = 0xFFFFFA
        else:
            bot_guild_member = await ctx.guild.fetch_member(self.bot.user.id)
            if len(str(bot_guild_member.colour.value)) == 1:
                colour = 0xFFFFFA
            else:
                colour = bot_guild_member.colour.value

        embed = discord.Embed(description="Last updated and effective as of **12th of August 2020 New Zealand Standard "
                                          "Time**.", colour=colour, title="CoffinBot Privacy Policy")

        embed.add_field(name="What data do we collect?", inline=False,
                        value="CoffinBot does not collect or store any user data.")

        embed.add_field(name="How can you contact us if you have questions?", inline=False,
                        value="If you have questions regarding your privacy, this privacy policy or this bot in "
                              "general you may contact me using one of the forms of contact listed below;"
                              "\n• Email - `cairoacason.john@gmail.com`\n• Discord - `Cairo#1123 (208105877838888960)`")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
