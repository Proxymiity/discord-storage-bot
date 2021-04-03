import re
from random import randint


async def valid_name(ctx, string):
    if not re.match('^[a-zA-Z0-9_]*$', string):
        await ctx.send("*AYAYA!* Name should follow this regex: `[a-zA-Z0-9_]`")
        return False
    else:
        return True


async def valid_name_extended(ctx, string):
    if not re.match('^[a-zA-Z0-9_.-]*$', string):
        await ctx.send("*AYAYA!* Name should follow this regex: `[a-zA-Z0-9_.-]`")
        return False
    else:
        return True


async def valid_path(ctx, string):
    if not re.match('^[a-zA-Z0-9_.\\-/\\\\:]*$', string):
        await ctx.send("*AYAYA!* Path should follow this regex: `[a-zA-Z0-9_.\\-/\\\\:]`")
        return False
    else:
        return True


def sanitize_name(string):
    if not re.match('^[a-zA-Z0-9_.-]*$', string):
        new = "".join(x for x in string if re.match('^[a-zA-Z0-9_.-]*$', x))
        if new == "":
            return f"invalid-{randint(1000, 9999)}"
        return new
    else:
        return string
