"""
This module exists purely to provide a global session for `aiohttp`.
"""


import asyncio
import atexit
from typing import Optional

import aiohttp
from loguru import logger

_g_session: Optional[aiohttp.ClientSession] = None
"""
Global session to use for aiohttp.
"""


async def get_session() -> aiohttp.ClientSession:
    """
    Returns:
        The global `aiohttp` session, creating it if necessary.

    """
    global _g_session
    if _g_session is None:
        logger.debug("Initializing aiohttp session.")
        _g_session = aiohttp.ClientSession()

    return _g_session


def _clean_up_session() -> None:
    """
    Exit handler that cleans up the aiohttp session.

    """
    if _g_session is not None:
        logger.debug("Cleaning up aiohttp session...")
        asyncio.run(_g_session.close())


atexit.register(_clean_up_session)
