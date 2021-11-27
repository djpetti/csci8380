"""
This module exists purely to provide a global driver for Neo4J.
"""


import atexit
from typing import Optional

from loguru import logger
from neo4j import Driver, GraphDatabase

_NEO4J_URL = "bolt://localhost:7687"
"""
URL to use for connecting to the Neo4J database.
"""
_NEO4J_USER = "neo4j"
"""
Username to use for connecting to the Neo4J database.
"""
_NEO4J_PASSWORD = "password"
"""
Password to use for connecting to the Neo4J database.
"""


_g_driver: Optional[Driver] = None
"""
Global driver to use for Neo4J.
"""


def get_driver() -> Driver:
    """
    Returns:
        The global Neo4J driver, creating it if necessary.

    """
    global _g_driver
    if _g_driver is None:
        logger.debug("Initializing Neo4J driver.")
        _g_driver = GraphDatabase.driver(
            _NEO4J_URL, auth=(_NEO4J_USER, _NEO4J_PASSWORD)
        )

    return _g_driver


def _clean_up_driver() -> None:
    """
    Exit handler that cleans up the Neo4J driver.

    """
    if _g_driver is not None:
        logger.debug("Cleaning up Neo4J driver...")
        _g_driver.close()


atexit.register(_clean_up_driver)
