from utils.dataIO import dataIO
ch_id = dataIO.load_json("data/storage.json")["storage"]["logs"]


async def send(cli, ctx=None, action=None, p1: str = None, p2: str = None, p3: str = None, done: bool = False):
    ch = await cli.fetch_channel(ch_id)
    msg = "Unknown log operation."
    if action == "create_pool":
        msg = f"Created pool `{p1}`"
    elif action == "categorize_pool":
        msg = f"Categorized pool `{p1}`"
    elif action == "delete_pool":
        msg = f"Deleted pool `{p1}`"
    elif action == "recycle_pool":
        msg = f"Emptied pools marked for deletion"
    elif action == "store_file":
        msg = f"Upload of `{p1}` in `{p2}` enqueued"
        if done:
            msg = f"Upload of `{p1}` in `{p2}` completed"
    elif action == "retrieve_file":
        msg = f"Download of `{p1}` from `{p2}` enqueued"
        if done:
            f"Download of `{p1}` from `{p2}` completed"
    elif action == "store_url":
        msg = f"Transfer of `{p1}` in `{p2}` as `{p3}` enqueued"
        if done:
            msg = f"Transfer of `{p1}` in `{p2}` as `{p3}` completed"
    elif action == "delete_file":
        msg = f"Deletion of `{p1}` from `{p2}` enqueued"
        if done:
            msg = f"Deletion of `{p1}` from `{p2}` completed"
    elif action == "yank_file":
        msg = f"Yanked `{p1}` from {p2}`"
    if ctx:
        u = ctx.message.author
        msg = f"`{u.name}#{u.discriminator}` " + msg
    await ch.send(msg)
