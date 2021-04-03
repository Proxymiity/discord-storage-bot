from discord.ext import commands
from utils.dataIO import dataIO
bot_owner_id = dataIO.load_json("data/config.json")["owner"]
auth_users = dataIO.load_json("data/storage.json")["users"]


def bot_owner():
    return commands.check(bot_owner_raw)


def bot_owner_raw(ctx):
    return ctx.message.author.id == bot_owner_id


def authorized():
    return commands.check(authorized_raw)


def authorized_raw(ctx):
    return ctx.message.author.id in auth_users
