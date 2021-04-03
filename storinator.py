import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import tools

config = dataIO.load_json("data/config.json")
token = config["token"]
prefix = config["prefix"]
bot = commands.Bot(prefix, intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.remove_command("help")
    for p in config["loadPlugins"]:
        print(f"Now loading plugin {p}")
        try:
            bot.load_extension(p)
        except commands.ExtensionAlreadyLoaded:
            pass
    await bot.change_presence(status=tools.get_status("online"),
                              activity=tools.get_presence("watch", "some files."))
    print("on_ready event completed!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("*Ayaya...* Can't use this command in a DM.")
    elif isinstance(error, commands.PrivateMessageOnly):
        await ctx.send("*Ayaya...* Can't use this command in a server.")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("*Ayaya...* Can't use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("*Ayaya?* Missing required argument.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("*Ayaya?* Unexpected and/or bad argument.")
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.Forbidden):
            await ctx.send("Random permission error occurred. Please set permissions to 8.")
        else:
            await ctx.send(f"Execution error: {error}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Ignoring 404 error. *This isn't an error.*")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("*AYAYA!!!* Command integrity check failure. Please check that you're correctly authenticated.")
    else:
        print(f"Uncaught exception {error}")
        dataIO.save_json("error.json", [error])
        await ctx.send("Uncaught general error and/or exception. Logged to console+file if possible.")


print(f"Logging in with token {token[0:5]}")
bot.run(token)
