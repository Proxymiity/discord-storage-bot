import requests
import os
import shutil
from pathlib import Path
from fsplit.filesplit import Filesplit
from random import randint
from utils import pool, verify
splitter = Filesplit()
g_tmp_path = Path(os.getcwd() + "/tmp")
shutil.rmtree(str(g_tmp_path))
os.mkdir(str(g_tmp_path))


async def store(cli, file: str, name: str, path, channel: int, size: int = 8000000, time_ctl: int = 1):
    files = []
    file_path = Path(path)
    tmp_dir = Path(os.getcwd() + f"/tmp/{file_path.name}-{randint(1000, 9999)}.tmp")
    os.mkdir(str(tmp_dir))
    splitter.split(file=path, split_size=size, output_dir=tmp_dir)
    for x in os.listdir(str(tmp_dir)):
        tmp_path = Path(str(tmp_dir) + "/" + x)
        files.append(str(tmp_path))
    await pool.store(cli, file, name, channel, files, time_ctl)
    shutil.rmtree(str(tmp_dir))


async def retrieve(cli, file: str, path, channel: int, time_ctl: int = 1):
    file_path = Path(path)
    tmp_dir = Path(os.getcwd() + f"/tmp/{file_path.name}-{randint(1000, 9999)}.tmp")
    os.mkdir(str(tmp_dir))
    await pool.retrieve(cli, file, channel, str(tmp_dir), time_ctl)
    splitter.merge(input_dir=tmp_dir, output_file=path)
    shutil.rmtree(str(tmp_dir))


async def download(cli, url: str, name: str, channel: int, size: int = 8000000, time_ctl: int = 1):
    file = verify.sanitize_name(url.rsplit("/", 1)[1])
    tmp_dir = Path(os.getcwd() + f"/tmp/{file}-{randint(1000, 9999)}.tmp")
    f_path = Path(str(tmp_dir) + f"/{file}")
    os.mkdir(str(tmp_dir))
    with requests.get(url) as r:
        with open(str(f_path), "wb") as f:
            f.write(r.content)
    await store(cli, file, name, f_path, channel, size, time_ctl)
    shutil.rmtree(str(tmp_dir))
