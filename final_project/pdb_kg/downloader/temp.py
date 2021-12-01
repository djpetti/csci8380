from download_manager import DownloadManager
from graph_db import update_entry, _to_cypher
import asyncio

dm = DownloadManager()
async_nodes = dm.download_all_nodes()


async def download_pdb():
    async for item in async_nodes:
        with open("pdb.txt", "a+") as f:
            f.write(_to_cypher(item) + "\n")

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(download_pdb())
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())  # see: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.shutdown_asyncgens
    loop.close()

