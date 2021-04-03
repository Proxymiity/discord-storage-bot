import discord
import time
from pathlib import Path
from utils.dataIO import dataIO
storage_settings = dataIO.load_json("data/storage.json")


async def new(cli, name: str):
    source = await create(cli, name)
    await categorize(cli, source.id)
    return source


async def create(cli, name: str):
    p = load()
    if name in p:
        return
    source = cli.get_guild(storage_settings["storage"]["server"])
    target = await source.create_text_channel(name)
    p[name] = {"files": {}, "id": target.id, "ct": None}
    save(p)
    return target


async def categorize(cli, channel: int, category: int = None, sync: bool = False):
    p = load()
    category = category or storage_settings["storage"]["categories"]["main"]
    source = await cli.fetch_channel(channel)
    destination = await cli.fetch_channel(category)
    await source.edit(category=destination, sync_permissions=sync)
    p[pool_by_id(channel)]["ct"] = category
    save(p)


async def recycle(cli, channel: int):
    await categorize(cli, channel, storage_settings["storage"]["categories"]["recycle"])


async def empty_recycle_bin(cli):
    p = load()
    to_recycle = []
    for x in p:
        if p[x]["ct"] == storage_settings["storage"]["categories"]["recycle"]:
            to_recycle.append(p[x]["id"])
    for x in to_recycle:
        await delete(cli, x)


async def delete(cli, channel: int):
    p = load()
    target = await cli.fetch_channel(channel)
    await target.delete()
    p.pop(pool_by_id(channel))
    save(p)


async def store(cli, file: str, name: str, channel: int, paths: list, time_ctl: int = 1, fpm: int = 1):
    p = load()
    cp = p[pool_by_id(channel)]["files"]
    sent = []
    target = await cli.fetch_channel(channel)
    sub_paths = [paths[x:x + fpm] for x in range(0, len(paths), fpm)]
    y = 0
    for x in sub_paths:
        files = [discord.File(z) for z in x]
        names = [f.filename for f in files]
        content = f"storage|{file}|{y}|{len(sub_paths)}~\n" \
                  f"File name: `{file}` - Custom name: `{name}`\n" \
                  f"Part {y+1} of {len(sub_paths)} - Contains {len(x)} file(s)\n" \
                  f"File(s): `{', '.join(names)}`"
        ms = await target.send(content=content, files=files)
        sent.append(ms.id)
        time.sleep(time_ctl)
        y += 1
    cp[file] = {"custom_name": name, "parts": sent}
    save(p)


async def retrieve(cli, file: str, channel: int, path: str, time_ctl: int = 1):
    p = load()
    cp = p[pool_by_id(channel)]["files"]
    msgs = cp[file]["parts"]
    target = await cli.fetch_channel(channel)
    for x in msgs:
        msg = await target.fetch_message(x)
        ats = msg.attachments
        for y in ats:
            tmp_path = Path(path + "/" + y.filename)
            await y.save(str(tmp_path))
            time.sleep(time_ctl)


async def yank(cli, file: str, channel: int, time_ctl: int = 1):
    p = load()
    cp = p[pool_by_id(channel)]["files"]
    target = await cli.fetch_channel(channel)
    for x in cp[file]["parts"]:
        msg = await target.fetch_message(x)
        await msg.delete()
        time.sleep(time_ctl)
    cp.pop(file)
    save(p)


def db_yank(file: str, channel: int):
    p = load()
    cp = p[pool_by_id(channel)]["files"]
    cp.pop(file)
    save(p)


def load():
    pool = dataIO.load_json("data/pools.json")
    return pool


def save(pool):
    dataIO.save_json("data/pools.json", pool)


def pool_by_id(_id: int):
    p = load()
    for x in p:
        if p[x]["id"] == _id:
            return x


def id_by_name(name: str):
    p = load()
    if name in p:
        return p[name]["id"]
