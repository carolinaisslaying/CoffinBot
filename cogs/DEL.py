import discord, aiohttp, json
from discord.ext import tasks, commands


class DEL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.del_update_stats.start()

    def cog_unload(self):
        self.del_update_stats.cancel()

    @tasks.loop(minutes=30.0)
    async def del_update_stats(self):
        """ This automatically updates your server count to Discord Extreme List every 30 minutes. """
        await self.bot.wait_until_ready()
        async with aiohttp.ClientSession() as session:
            async with session.post(f'https://api.discordextremelist.xyz/v2/bot/{self.bot.user.id}/stats',
                                    headers={"Authorization": self.bot.settings["del_token"],
                                             "Content-Type": 'application/json'},
                                    data=json.dumps({"guildCount": len(self.bot.guilds),
                                                     "shardCount": len(self.bot.shard_id)})
                                    ) as r:
                js = await r.json()
                if js["error"]:
                    print(f"Failed to post to discordextremelist.xyz\n{js}")


def setup(bot):
    bot.add_cog(DEL(bot))
