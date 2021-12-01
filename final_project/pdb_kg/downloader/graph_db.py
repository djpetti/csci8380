"""
Contains low-level functions for interfacing with the graph database.
"""
import asyncio
from functools import singledispatch
from typing import Any, List, Set, Tuple
from uuid import UUID
from loguru import logger

from neo4j import Transaction, Result

from ..data_model import EntryNode, NodeBase, NodeLabel, AnnotationNode, ProteinNode
from ..neo4j_driver import get_driver


@singledispatch
def _to_cypher(value: Any, **kwargs: Any) -> str:
    """
    Converts a value to its equivalent form in a Cypher query.

    Args:
        value: The value to convert.
        **kwargs: Possible custom keyword arguments for this function.

    Returns:
        The converted value, as a string that can be included in a query.

    """


@_to_cypher.register
def _(value: str) -> str:
    return f"'{value}'"


@_to_cypher.register
def _(value: int) -> str:
    return str(value)


@_to_cypher.register
def _(value: UUID) -> str:
    return _to_cypher(str(value))


@_to_cypher.register(list)
def _(value: List[Any]) -> str:
    list_items = [_to_cypher(i) for i in value]
    list_items = ",".join(list_items)
    return f"[{list_items}]"


@_to_cypher.register(tuple)
def _(value: Tuple[Any, ...]) -> str:
    # Treat this as a list.
    return _to_cypher(list(value))


@_to_cypher.register(set)
def _(value: Set[Any]) -> str:
    # Treat this as a list.
    return _to_cypher(list(value))


@_to_cypher.register
def _(value: NodeBase, include_uuid: bool = False) -> str:
    """
    Args:
        value: The node to convert.
        include_uuid: If true, include the UUID in the resulting structure.
            Otherwise, it will be left out.

    Returns:
        The Cypher mapping corresponding to this node structure.

    """
    exclude_set = {"label"}
    if not include_uuid:
        exclude_set.add("uuid")
    node_attributes = value.dict(exclude=exclude_set)

    # Create the mapping.
    cypher_attributes = {k: _to_cypher(v) for k, v in node_attributes.items()}
    cypher_pairs = [": ".join(item) for item in cypher_attributes.items()]
    mapping_items = ", ".join(cypher_pairs)
    return f"{{{mapping_items}}}"


def _update_entry_transaction(
    transaction: Transaction, entry: EntryNode
) -> None:
    """
    Transaction function that updates (or creates) an entry node.

    Args:
        transaction: The transaction object.
        entry: The entry information.

    """
    transaction.run(
        f"MERGE (entry:{entry.label.name} {{uuid: $uuid}})"
        f"SET entry += {_to_cypher(entry)}",
        uuid=str(entry.uuid),
    )


def fetch_read(fn, *args) -> Result:
    """
    Shortcut for a read request for the current database.

    Args:
        fn: Function that should be called for the read request. First argument
        of the function should always be of they type Transaction.
        *args: List of accompanying arguments for the function above.

    """
    with get_driver().session() as session:
        return session.read_transaction(
            fn, *args
        )


def run_read_query(query: str) -> Result:
    """
    Runs a query with a simple read request. This function helps to remove
    boilerplate.

    Args:
        query: The query to be ran.
    """

    def _rt(transaction: Transaction, ts: str):
        logger.debug(f"Running transaction {query}")
        return transaction.run(ts)
    return fetch_read(_rt, query)


def simple_get_transaction(label, uuid: UUID) -> Result:
    """
    Runs a simple get request using any of the labellings from the Label class
    and the uuid corresponding to the element to be retrieved.

    Args:
        label: Element from the Label enumeration
        uuid: A UUID corresponding to the element to be retrieved.

    """

    transaction = f"MATCH (entry:{label.name} {{uuid: '{uuid}'}}) RETURN entry"
    return run_read_query(transaction)


def arun(fn, *args):
    """
    asyncio.to_thread wasn't working for myversion of python, so this is the
    alternative method which has worked fine in my case. Provides a shortcut
    with less boilerplate.

    Args:
        fn: Function to be waited on for completion
        *args: List of the arguments to this function

    """
    return asyncio.get_running_loop().run_in_executor(None, fn, *args)


async def update_entry(entry: EntryNode) -> None:
    """
    Updates or creates a particular entry node.

    Notes:
        The synchronous database access is performed in a separate thread.

    Args:
        entry: The entry information.

    """

    def _update_entry_sync(_entry: EntryNode) -> None:
        with get_driver().session() as session:
            session.write_transaction(_update_entry_transaction, _entry)

    await arun(_update_entry_sync, entry)


async def get_entry(entry_uuid: UUID) -> EntryNode:
    """
    Fetches a particular entry node by UUID.

    Args:
        entry_uuid: The UUID of the entry.

    Notes:
        The synchronous database access is performed in a separate thread.

    Returns:
        The resulting entry node.

    """

    node_info = await arun(simple_get_transaction, Label.ENTRY, entry_uuid)
    node_info = node_info.single()[0]
    # Convert to an EntryNode structure.
    return EntryNode(**node_info)


async def get_annotation(annotation_id: UUID) -> AnnotationNode:
    node_info = await arun(simple_get_transaction, Label.ANNOTATION, annotation_id)
    node_info = node_info.single()[0]
    logger.debug(node_info)
    # Convert to an EntryNode structure.
    return AnnotationNode(**node_info)


async def get_protein(protein_id: UUID) -> ProteinNode:
    node_info = await arun(simple_get_transaction, Label.PROTEIN, protein_id)
    node_info = node_info.single()[0]
    logger.debug(node_info)
    return ProteinNode(**node_info)

