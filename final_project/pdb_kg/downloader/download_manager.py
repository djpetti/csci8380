"""
Manages the downloading of datasets from PDB.
"""


import asyncio
import time
from typing import Any, AsyncIterator, Awaitable, Coroutine, Iterable

from loguru import logger
from pydantic import BaseModel

from .data_model import EntryCommon, EntryNode, ProteinNode
from .download_tasks import get_entry, get_entry_list, get_protein_entity


class DownloadManager:
    """
    Manages the downloading of datasets from PDB.
    """

    _ENTRY_TASK_BATCH_SIZE = 100
    """
    Number of entry download tasks to deploy at once.
    """

    def __init__(
        self,
        max_concurrent_downloads: int = 10,
        max_requests_per_second: int = 50,
    ):
        """
        Args:
            max_concurrent_downloads: Maximum number of concurrent downloads
                that we allow.
            max_requests_per_second: Maximum number of requests to make per
                second to the PDB API.
        """
        self.__min_request_period = 1.0 / max_requests_per_second
        self.__download_semaphore = asyncio.Semaphore(max_concurrent_downloads)

        # Time at which the last download task was dispatched.
        self.__last_download_time = time.time()

    def __do_download(self, download_coro: Coroutine) -> asyncio.Task:
        """
        Runs a download concurrently, and returns the resulting task.

        Args:
            download_coro: The download coroutine to run.

        Returns:
            The associated task.

        """

        async def _safe_download() -> Any:
            """
            Internal function that safely runs the download after making sure
            we're not running two many concurrently.

            Returns:
                The result of the download coroutine.

            """
            async with self.__download_semaphore:
                # Apply rate limiting.
                while (
                    time.time() - self.__last_download_time
                    < self.__min_request_period
                ):
                    delay_time = self.__min_request_period - (
                        time.time() - self.__last_download_time
                    )
                    await asyncio.sleep(delay_time)
                self.__last_download_time = time.time()
                logger.debug("Download time: {}", self.__last_download_time)

                return await download_coro

        return asyncio.create_task(_safe_download())

    @staticmethod
    async def __await_concurrently(
        awaitables: Iterable[Awaitable],
    ) -> AsyncIterator[Any]:
        """
        Concurrently waits on a set of awaitable objects, and yields the
        results in the order that they become available.

        Args:
            awaitables: The awaitable objects.

        Returns:
            The results from each object, in any order.

        """
        pending = awaitables
        while len(pending) != 0:
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )

            for awaitable in done:
                yield awaitable

    @staticmethod
    async def __download_entry_ids() -> AsyncIterator[str]:
        """
        Downloads all the entry IDs from PDB.

        Yields:
            The downloaded IDs.

        """
        entry_ids = await get_entry_list()
        for entry_id in entry_ids:
            yield entry_id

    async def __download_entries(
        self,
        entry_ids: AsyncIterator[str],
    ) -> AsyncIterator[EntryNode]:
        """
        Downloads all the entry information for a set of entry IDs.

        Args:
            entry_ids: The entry IDs to download info for.

        Yields:
            The node info for each entry.

        """
        entry_tasks = []
        async for entry_id in entry_ids:
            # Deploy tasks in smaller batches in order to limit memory usage.
            if len(entry_tasks) < self._ENTRY_TASK_BATCH_SIZE:
                entry_tasks.append(self.__do_download(get_entry(entry_id)))
                continue

            async for entry_task in self.__await_concurrently(entry_tasks):
                yield entry_task.result()
            entry_tasks = []

        # Handle any remaining tasks.
        async for entry_task in self.__await_concurrently(entry_tasks):
            yield entry_task.result()

    async def __download_protein_entities(
        self,
        entry: EntryCommon,
    ) -> AsyncIterator[ProteinNode]:
        """
        Downloads all the protein entity information from a particular entry.

        Args:
            entry: The entry to download information for.

        Yields:
            The node info for each protein.

        """
        entity_tasks = [
            self.__do_download(
                get_protein_entity(entry_id=entry.entry_id, entity_id=entity)
            )
            for entity in entry.protein_entity_ids
        ]

        async for entity_task in self.__await_concurrently(entity_tasks):
            yield entity_task.result()

    async def download_all_nodes(self) -> AsyncIterator[BaseModel]:
        """
        Downloads every single node in the knowledge graph.

        Yields:
            Each node that it downloads.

        """
        # First, get the IDs of the entries to download.
        entry_ids = self.__download_entry_ids()
        # Now, get the actual entry data.
        entries = self.__download_entries(entry_ids)

        # Finally, get the entity data for each entry.
        async for entry in entries:
            yield entry

            async for entity in self.__download_protein_entities(entry):
                yield entity
