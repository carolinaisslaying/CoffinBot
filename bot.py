import colouredlogs, logging
import datetime
import discord
import json

from colorama import init
from discord.ext import commands, tasks

init()
colouredlogs.install()

with open("settings.json") as content:
    settings = json.load(content)

logging.basicConfig(level=logging.INFO)

logging.info("Starting bot")
botExtensions = [
    "cogs.playback",
    "jishaku"
]


async def get_prefix(bot, message):
    if not message.guild:
        prefixes = ""
        return prefixes
    else:
        return settings["prefix"]


bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, owner_id=settings["owner"],
                   allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
bot.settings = settings

if __name__ == "__main__":
    for ext in botExtensions:
        try:
            bot.load_extension(ext)
            logging.info(f"{ext} has been loaded")
        except Exception as err:
            logging.error(f"An error occurred whilst loading {ext}: {err}")


@bot.event
async def on_ready():
    logging.info(f"Connection established! - Logged in as {bot.user} ({bot.user.id})")

    if not hasattr(bot, "uptime"):
        bot.uptime = datetime.datetime.utcnow()

    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=3, name="coffin dances"))


@bot.event
async def on_guild_join(guild):
    logging.info(f"Joined guild - {guild.name} ({guild.id})")

bot.run(settings["token"], bot=True, reconnect=True)
