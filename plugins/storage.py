from discord import File
from os import getcwd
from pathlib import Path
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks, tools, pool, file, verify, log
storage_settings = dataIO.load_json("data/storage.json")


class Storage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.locked = False

    async def check_locked(self, ctx):
        if self.locked:
            await ctx.send("*AYAYA!!* Database is locked. Perhaps a transfer is still going?\n"
                           "Please wait before executing this command, or check "
                           f"<#{storage_settings['storage']['logs']}> for info.")
        return self.locked

    @checks.authorized()
    @commands.command(name="help")
    async def _help(self, ctx):
        p = Path(getcwd() + "/help.md")
        h = File(str(p))
        await ctx.send(file=h)

    @checks.authorized()
    @commands.group(aliases=["p"])
    async def pool(self, ctx):
        pass

    @checks.authorized()
    @pool.command()
    async def create(self, ctx, name: str):
        if await self.check_locked(ctx):
            return
        name = name.lower()
        if not await verify.valid_name(ctx, name):
            return
        await pool.new(self.bot, name)
        await ctx.send(f"Created new pool named `{name}`")
        await log.send(self.bot, ctx, "create_pool", name)

    @checks.authorized()
    @pool.command()
    async def recycle(self, ctx, name: str):
        if await self.check_locked(ctx):
            return
        name = name.lower()
        if not await verify.valid_name(ctx, name):
            return
        p = pool.load()
        if name not in p:
            await ctx.send("*A-Ayaya..?* Pool does not exist.")
            return
        pool_id = pool.id_by_name(name)
        await pool.recycle(self.bot, pool_id)
        await ctx.send("Sent the pool to the Recycle Bin.")
        await log.send(self.bot, ctx, "categorize_pool", name)

    @checks.authorized()
    @pool.command()
    async def restore(self, ctx, name: str):
        if await self.check_locked(ctx):
            return
        name = name.lower()
        if not await verify.valid_name(ctx, name):
            return
        p = pool.load()
        if name not in p:
            await ctx.send("*A-Ayaya..? Pool does not exist.*")
            return
        if p[name]["ct"] == storage_settings["storage"]["categories"]["main"]:
            await ctx.send("*A-Ayaya..? Pool isn't in the Recycle Bin.*")
            return
        pool_id = pool.id_by_name(name)
        await pool.categorize(self.bot, pool_id, storage_settings["storage"]["categories"]["main"])
        await ctx.send("Restored the pool!")
        await log.send(self.bot, ctx, "categorize_pool", name)

    @checks.authorized()
    @pool.command(name="delete")
    async def _del(self, ctx, name: str):
        name = name.lower()
        if not await verify.valid_name(ctx, name):
            return
        p = pool.load()
        if name not in p:
            await ctx.send("*A-Ayaya..? Pool does not exist.*")
            return
        pool_id = pool.id_by_name(name)
        await pool.delete(self.bot, pool_id)
        await ctx.send("Deleted the pool!")
        await log.send(self.bot, ctx, "delete_pool", name)

    @checks.authorized()
    @pool.command()
    async def empty_recycle(self, ctx):
        if await self.check_locked(ctx):
            return
        await pool.empty_recycle_bin(self.bot)
        await ctx.send("Emptied the Recycle Bin.")
        await log.send(self.bot, ctx, "recycle_pool")

    @checks.authorized()
    @commands.group(aliases=["f"])
    async def file(self, ctx):
        pass

    @checks.authorized()
    @file.command(aliases=["s"])
    async def store(self, ctx, ch: str, path: str, *, name: str = None):
        if await self.check_locked(ctx):
            return
        p = pool.load()
        ch = ch.lower()
        local_file = Path(path)
        pl = pool.id_by_name(ch)
        if not await verify.valid_name(ctx, ch) or not await verify.valid_path(ctx, path):
            return
        if not pl:
            await ctx.send("*AYAYA!* There's no storage pool with that name.")
            return
        if await self.is_ro(ctx, p, ch):
            return
        if local_file.name in p[ch]["files"]:
            await ctx.send("*A-Ayaya..?* There's already a file with that name.")
            return
        if not local_file.is_file():
            await ctx.send("*A-Ayaya..?* There's no file at the provided location.")
            return
        name = name or local_file.stem
        msg = await ctx.send("*yawn* Encrypting/Splitting/Uploading that file...")
        self.locked = True
        await log.send(self.bot, ctx, "store_file", local_file.name, ch)
        if p[ch]["ct"] == storage_settings["storage"]["categories"]["recycle"]:
            return
        await file.store(self.bot, local_file.name, name, str(local_file), pl)
        self.locked = False
        await msg.delete()
        await ctx.message.reply(f"Successfully uploaded `{local_file.name}` to `{ch}`.\n"
                                f"Get it back using `/file retrieve {ch} {local_file.name} <dl path>`.")
        await log.send(self.bot, ctx, "store_file", local_file.name, ch, done=True)

    @checks.authorized()
    @file.command(aliases=["r"])
    async def retrieve(self, ctx, ch: str, name: str, path: str):
        p = pool.load()
        ch = ch.lower()
        local_file = Path(path)
        pl = pool.id_by_name(ch)
        if await self.check_locked(ctx) or not await verify.valid_name(ctx, ch):
            return
        if not await verify.valid_path(ctx, path) or not await verify.valid_name_extended(ctx, name):
            return
        if not pl:
            await ctx.send("*AYAYA!* There's no storage pool with that name.")
            return
        if await self.is_ro(ctx, p, ch):
            return
        if name not in p[ch]["files"]:
            await ctx.send("*A-Ayaya..?* There's no file to retrieve with that name.")
            return
        if local_file.exists():
            await ctx.send("*A-Ayaya..?* There's already a file at the provided location.")
            return
        msg = await ctx.send("*yawn* Downloading/Merging/Decrypting that file...")
        self.locked = True
        await log.send(self.bot, ctx, "retrieve_file", name, ch)
        await file.retrieve(self.bot, name, path, pl)
        self.locked = False
        await msg.delete()
        await ctx.message.reply(f"Successfully downloaded `{local_file.name}` to `{path}`.")
        await log.send(self.bot, ctx, "retrieve_file", name, ch, done=True)

    @checks.authorized()
    @file.command(aliases=["dl"])
    async def download(self, ctx, ch: str, url: str, *, name: str = None):
        if await self.check_locked(ctx):
            return
        p = pool.load()
        ch = ch.lower()
        f = verify.sanitize_name(url.rsplit("/", 1)[1])
        pl = pool.id_by_name(ch)
        if not await verify.valid_name(ctx, ch):
            return
        if not pl:
            await ctx.send("*AYAYA!* There's no storage pool with that name.")
            return
        if await self.is_ro(ctx, p, ch):
            return
        if f in p[ch]["files"]:
            await ctx.send("*A-Ayaya..?* There's already a file with that name.")
            return
        name = name or f.rsplit(".", 1)[0]
        msg = await ctx.send("*yawn* Encrypting/Splitting/Transferring that file...")
        self.locked = True
        await log.send(self.bot, ctx, "store_url", url, ch, f)
        await file.download(self.bot, url, name, pl)
        self.locked = False
        await msg.delete()
        await ctx.message.reply(f"Successfully transferred `{f}` to `{ch}`.\n"
                                f"Get it back using `/file retrieve {ch} {f} <dl path>`.")
        await log.send(self.bot, ctx, "store_url", url, ch, f, done=True)

    @checks.authorized()
    @file.command(aliases=["d"])
    async def delete(self, ctx, ch: str, name: str):
        p = pool.load()
        if await self.check_locked(ctx):
            return
        ch = ch.lower()
        pl = pool.id_by_name(ch)
        if not await verify.valid_name(ctx, ch) or not await verify.valid_name_extended(ctx, name):
            return
        if not pl:
            await ctx.send("*AYAYA!* There's no storage pool with that name.")
            return
        if await self.is_ro(ctx, p, ch):
            return
        if not await self.pre_del_check(ctx, ch, name):
            return
        msg = await ctx.send("*yawn* Deleting that file...")
        self.locked = True
        await log.send(self.bot, ctx, "delete_file", name, ch)
        await pool.yank(self.bot, name, pl)
        self.locked = False
        await msg.delete()
        await ctx.message.reply(f"Successfully deleted `{name}` from `{ch}`.")
        await log.send(self.bot, ctx, "delete_file", name, ch, done=True)

    @checks.authorized()
    @file.command(aliases=["y"])
    async def yank(self, ctx, ch: str, name: str):
        p = pool.load()
        ch = ch.lower()
        pl = pool.id_by_name(ch)
        if await self.check_locked(ctx) or not await verify.valid_name(ctx, ch):
            return
        if not pl:
            await ctx.send("*AYAYA!* There's no storage pool with that name.")
            return
        if await self.is_ro(ctx, p, ch):
            return
        if not await verify.valid_name_extended(ctx, name) or not await self.pre_del_check(ctx, ch, name):
            return
        msg = await ctx.send("*yawn* Yanking that file...")
        pool.db_yank(name, pl)
        await msg.delete()
        await ctx.message.reply(f"Successfully yanked `{name}` from `{ch}`.")
        await log.send(self.bot, ctx, "yank_file", name, ch)

    @staticmethod
    async def pre_del_check(ctx, ch: str, name: str):
        p = pool.load()
        pl = pool.id_by_name(ch)
        if not pl:
            await ctx.send("*AYAYA!* There's no storage pool with that name.")
            return False
        if name not in p[ch]["files"]:
            await ctx.send("*A-Ayaya..?* There's no file with that name.")
            return False
        return True

    @checks.authorized()
    @commands.group(aliases=["s"])
    async def search(self, ctx):
        pass

    @checks.authorized()
    @search.command(aliases=["f"], name="file")
    async def search_file(self, ctx, ch: str, q: str):
        p = pool.load()
        ch = ch.lower()
        pl = pool.id_by_name(ch)
        if not pl:
            await ctx.send("*AYAYA!* There's no storage pool with that name.")
            return False
        files = p[ch]["files"]
        found = []
        for x in files:
            if q in x:
                found.append([f"`{x}`", f"custom name: `{files[x]['custom_name']}`, splits: {len(files[x]['parts'])}"])
        if found:
            to_send = tools.paginate_text(found, "", "", f"Found {len(found)} file(s):", mid_sep=", ")
            for x in to_send:
                await ctx.send(x)
        else:
            await ctx.send("*Ayaya...* No items matched your query.")

    @checks.authorized()
    @search.command(aliases=["n"], name="name")
    async def search_name(self, ctx, ch: str, *, q: str):
        p = pool.load()
        ch = ch.lower()
        pl = pool.id_by_name(ch)
        if not pl:
            await ctx.send("*AYAYA!* There's no storage pool with that name.")
            return False
        names = {}
        for f in p[ch]["files"]:
            names[f] = p[ch]["files"][f]["custom_name"]
        files = p[ch]["files"]
        found = []
        for x in names:
            if q in names[x]:
                found.append([f"`{x}`", f"custom name: `{files[x]['custom_name']}`, splits: {len(files[x]['parts'])}"])
        if found:
            to_send = tools.paginate_text(found, "", "", f"Found {len(found)} file(s):", mid_sep=", ")
            for x in to_send:
                await ctx.send(x)
        else:
            await ctx.send("*Ayaya...* No items matched your query.")

    @checks.authorized()
    @commands.group(aliases=["gs"])
    async def gsearch(self, ctx):
        pass

    @checks.authorized()
    @gsearch.command(aliases=["f"], name="file")
    async def search_file(self, ctx, q: str):
        p = pool.load()
        found = []
        for x in p:
            files = p[x]["files"]
            for y in files:
                if q in y:
                    found.append([f"`{x}`/`{y}`", f"custom name: `{files[y]['custom_name']}`, splits: "
                                                  f"{len(files[y]['parts'])}"])
        if found:
            to_send = tools.paginate_text(found, "", "", f"Found {len(found)} file(s):", mid_sep=", ")
            for x in to_send:
                await ctx.send(x)
        else:
            await ctx.send("*Ayaya...* No items matched your query.")

    @checks.authorized()
    @gsearch.command(aliases=["n"], name="name")
    async def search_name(self, ctx, *, q: str):
        p = pool.load()
        found = []
        for x in p:
            names = {}
            for f in p[x]["files"]:
                names[f] = p[x]["files"][f]["custom_name"]
            files = p[x]["files"]
            for y in names:
                if q in names[y]:
                    found.append([f"`{x}`/`{y}`", f"custom name: `{files[y]['custom_name']}`, splits: "
                                                  f"{len(files[y]['parts'])}"])
        if found:
            to_send = tools.paginate_text(found, "", "", f"Found {len(found)} file(s):", mid_sep=", ")
            for x in to_send:
                await ctx.send(x)
        else:
            await ctx.send("*Ayaya...* No items matched your query.")

    @checks.authorized()
    @commands.command(aliases=["l"], name="list")
    async def list(self, ctx, *, ch: str = None):
        p = pool.load()
        found = []
        if ch:
            ch = ch.lower()
            files = p[ch]["files"]
            for x in files:
                found.append([f"`{x}`", f"custom name: `{files[x]['custom_name']}`, splits: "
                                        f"{len(files[x]['parts'])}"])
        else:
            for x in p:
                files = p[x]["files"]
                for y in files:
                    found.append([f"`{x}`/`{y}`", f"custom name: `{files[y]['custom_name']}`, splits: "
                                                  f"{len(files[y]['parts'])}"])
        if found:
            to_send = tools.paginate_text(found, "", "", f"Found {len(found)} file(s):", mid_sep=", ")
            for x in to_send:
                await ctx.send(x)
        else:
            await ctx.send("*Ayaya...* No items found in the storage.")

    @staticmethod
    async def is_ro(ctx, p, ch: str):
        if p[ch]["ct"] == storage_settings["storage"]["categories"]["recycle"]:
            await ctx.send("*...Ayaya?* This pool is in the Recycle Bin and is read-only.")
            return True
        return False


def setup(bot):
    plugin = Storage(bot)
    bot.add_cog(plugin)
