"""
Contains low-level functions for interfacing with the graph database.
"""
import asyncio
from functools import singledispatch
from typing import Any, List, Set, Tuple
from uuid import UUID

from neo4j import Transaction
from neo4j.graph import Node

from .data_model import EntryNode, Label, NodeBase
from .neo4j_driver import get_driver


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


def _get_entry_transaction(transaction: Transaction, entry_uuid: UUID) -> Node:
    """
    Transaction function that loads a particular entry node.

    Args:
        transaction: The transaction object.
        entry_uuid: The entry UUID.

    Returns:
        The loaded entry.

    """
    result = transaction.run(
        f"MATCH (entry:{Label.ENTRY.name} {{uuid: $uuid}})" f"RETURN entry",
        uuid=str(entry_uuid),
    )
    return result.single()[0]


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

    await asyncio.to_thread(_update_entry_sync, entry)


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

    def _get_entry_sync(_entry_uuid: UUID) -> Node:
        with get_driver().session() as session:
            return session.read_transaction(
                _get_entry_transaction, _entry_uuid
            )

    node_info = await asyncio.to_thread(_get_entry_sync, entry_uuid)
    # Convert to an EntryNode structure.
    return EntryNode(**node_info)
