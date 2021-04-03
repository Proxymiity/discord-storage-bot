import discord
from discord.ext import commands
from utils import checks, tools
from utils.dataIO import dataIO


class Core(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @checks.bot_owner()
    @commands.command()
    async def shutdown(self, ctx, opt="normal"):
        print("Shutting down")
        await ctx.send("*Client shutting down...*")
        await self.bot.change_presence(status=tools.get_status("offline"))
        if "kill" in opt:
            exit(-1)
        else:
            await self.bot.logout()

    @checks.bot_owner()
    @commands.command()
    async def auth(self, ctx, uid: int):
        data = dataIO.load_json("data/storage.json")
        auths = data["users"]
        if uid in auths:
            await ctx.send("ID already in authorized users.")
            return
        auths.append(uid)
        await ctx.send("ID added to database.")
        dataIO.save_json("data/storage.json", data)

    @checks.bot_owner()
    @commands.command(name="deauth")
    async def de_auth(self, ctx, uid: int):
        data = dataIO.load_json("data/storage.json")
        auths = data["users"]
        if uid not in auths:
            await ctx.send("ID not in authorized users.")
            return
        auths.remove(uid)
        await ctx.send("ID removed from database.")
        dataIO.save_json("data/storage.json", data)

    @checks.bot_owner()
    @commands.command(name="auths")
    async def auths(self, ctx):
        data = dataIO.load_json("data/storage.json")
        auths = data["users"]
        users = []
        for x in auths:
            try:
                u = await self.bot.fetch_user(x)
                users.append([f"`{x}`", f"`{u.name}#{u.discriminator}`"])
            except discord.NotFound:
                await ctx.send(f"Removed {x} as it is no longer fetch-able.")
                auths.remove(x)
        if users:
            to_send = tools.paginate_text(users, "", "", f"Found {len(users)} user(s):")
            for x in to_send:
                await ctx.send(x)
        else:
            await ctx.send("No users authenticated.")
        dataIO.save_json("data/storage.json", data)


def setup(bot):
    plugin = Core(bot)
    bot.add_cog(plugin)
