"""
Contains low-level functions for interfacing with the graph database.
"""
import asyncio
from functools import singledispatch
from typing import Any, List, Set, Tuple
from uuid import UUID

from loguru import logger
from neo4j import Result, Transaction

from ..data_model import (
    AnnotationNode,
    EntryNode,
    NodeBase,
    NodeLabel,
    ProteinNode,
)
from ..neo4j_driver import get_driver
from .download_tasks import get_entry, get_entry_list, get_protein_entity


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
    # Remove quotes in the string.
    value = value.replace('"', "")
    return f'"{value}"'


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
        return session.read_transaction(fn, *args)


def run_read_query(query: str) -> Result:
    """
    Runs a query with a simple read request. This function helps to remove
    boilerplate.

    Args:
        query: The query to be run.
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


def run_in_thread(fn, *args):
    """
    Runs a function in a separate thread, without blocking the event loop.

    Args:
        fn: Function to be waited on for completion
        *args: List of the arguments to this function

    """
    return asyncio.get_running_loop().run_in_executor(None, fn, *args)


async def update_node(entry: NodeBase) -> None:
    """
    Updates or creates a particular node.

    Notes:
        The synchronous database access is performed in a separate thread.

    Args:
        entry: The entry information.

    """

    def _update_entry_sync(_entry: EntryNode) -> None:
        with get_driver().session() as session:
            session.write_transaction(_update_entry_transaction, _entry)

    await run_in_thread(_update_entry_sync, entry)


async def get_entry_2(entry_uuid: UUID) -> EntryNode:
    """
    Fetches a particular entry node by UUID.

    Args:
        entry_uuid: The UUID of the entry.

    Notes:
        The synchronous database access is performed in a separate thread.

    Returns:
        The resulting entry node.

    """

    node_info = await run_in_thread(
        simple_get_transaction, NodeLabel.ENTRY, entry_uuid
    )
    node_info = node_info.single()[0]
    # Convert to an EntryNode structure.
    return EntryNode(**node_info)


async def get_annotation(annotation_id: UUID) -> AnnotationNode:
    node_info = await run_in_thread(
        simple_get_transaction, NodeLabel.ANNOTATION, annotation_id
    )
    node_info = node_info.single()[0]
    logger.debug(node_info)
    # Convert to an EntryNode structure.
    return AnnotationNode(**node_info)


async def get_protein(protein_id: UUID) -> ProteinNode:
    node_info = await run_in_thread(
        simple_get_transaction, NodeLabel.PROTEIN, protein_id
    )
    node_info = node_info.single()[0]
    logger.debug(node_info)
    return ProteinNode(**node_info)


async def get_neighbors(object_id: UUID) -> List[NodeBase]:
    query = f'MATCH ({{uuid: "{object_id}"}})-[*1]-(c) RETURN c'
    node_info = await run_in_thread(run_read_query, query)

    # Return the list of items obtained by node_info. Needs to be wrapped in a
    # list since the default return value is an ItemView. Each of the items
    # needs to also be converted from a Node to a NodeBase (or possibly further
    # converted if necessary). Note that node_info.values() may need to be used
    # instead of node_info.items(), but that has yet to be tested.
    node_info = list(node_info.graph().nodes.items())
    node_info = [NodeBase(**node) for node in node_info]

    return node_info


async def get_annotated(annotation_id: UUID) -> List[ProteinNode]:
    query = (
        f'MATCH ({{uuid: "{annotation_id}"}})'
        f"-[*1]-(c:{NodeLabel.PROTEIN.name}) RETURN c"
    )
    node_info = await run_in_thread(run_read_query, query)

    # Return the list of items obtained by node_info. Needs to be wrapped in a
    # list since the default return value is an ItemView. Each of the items
    # needs to also be converted from a Node to a NodeBase (or possibly further
    # converted if necessary). Note that node_info.values() may need to be used
    # instead of node_info.items(), but that has yet to be tested.
    node_info = list(node_info.graph().nodes.items())
    node_info = [ProteinNode(**node) for node in node_info]
    return node_info


async def get_path(start: UUID, end: UUID, max_length: int) -> List[NodeBase]:
    query = (
        f"MATCH "
        f'(a {{uuid: "{start}"}}), '
        f'(b {{uuid: "{end}"}}), '
        f"p=shortestPath((a)-[*]-(b)) "
        f"WHERE length(p) > 1 AND length(p) < {max_length} "
        f"RETURN p"
    )
    node_info = await run_in_thread(run_read_query, query)

    # Return the list of items obtained by node_info. Needs to be wrapped in a
    # list since the default return value is an ItemView. Each of the items
    # needs to also be converted from a Node to a NodeBase (or possibly further
    # converted if necessary). Note that node_info.values() may need to be used
    # instead of node_info.items(), but that has yet to be tested.
    node_info = list(node_info.graph().nodes.items())
    node_info = [NodeBase(**node) for node in node_info]
    return node_info


async def do_query(cql: str) -> None:
    """
    Run a particular cypher through inputting custom query sentence.

    Args:
        cql: The created query sentence under NEO4J format.

    """

    with get_driver().session() as session:
        session.run(cql)


async def create_relationship(e1: object, e2: object, relation: str):
    """
    Create a relationship between two existed nodes(entities) by using Neo4J
    query sentence.

    Args:
        e1: Entity 1.
        e2: Entity 2.
        relation: Relation name.

    """

    cql = (
        "MATCH (a:" + e1.label.name + "), (b:" + e2.label.name + ") "
        "WHERE a.uuid = '"
        + str(e1.uuid)
        + "' AND b.uuid = '"
        + str(e2.uuid)
        + "' "
        "CREATE (a)-[:" + relation + "]->(b)"
    )

    await do_query(cql)


async def form_kg() -> None:
    """
    Create Neo4J database by adding nodes and relationships.

    Returns: None

    """

    entry_list = await get_entry_list()

    # get each entry in entry list
    for entry_id in entry_list:
        entry = await get_entry(entry_id=entry_id)
        await update_node(entry)

        # drug part
        # await get_drug_entity()

        # get each protein which belongs to a specific entry
        for prot_entity in entry.protein_entity_ids:
            prot_list = []
            (
                prot_node,
                host_organ_node,
                source_organ_node,
                db_node,
                anno_node,
            ) = await get_protein_entity(
                entry_id=entry_id, entity_id=prot_entity
            )

            await update_node(prot_node)
            await create_relationship(entry, prot_node, "HAS_PROTEIN")
            for ho in host_organ_node:
                await update_node(ho)
                await create_relationship(prot_node, ho, "HOST_ON")
            for so in source_organ_node:
                await update_node(so)
                await create_relationship(prot_node, so, "SOURCE_FROM")
            for db in db_node:
                await update_node(db)
                await create_relationship(prot_node, db, "REFER_TO")
            for anno in anno_node:
                await update_node(anno)
                await create_relationship(prot_node, anno, "HAS_ANNOTATION")

            # Create relationship between nodes have similar sequence
            if len(prot_list) > 1:
                for prev_prot in prot_list:
                    await create_relationship(
                        prev_prot, prot_node, "SIMILAR_SEQUENCE"
                    )
                    await create_relationship(
                        prot_node, prev_prot, "SIMILAR_SEQUENCE"
                    )
            prot_list.append(prot_node)


def save_kg_to_json(filename: str) -> None:
    """
    Export data in Neo4J into a JSON format file.

    Args:
        filename: Give a string type file name.

    """

    cql = "CALL apoc.export.json.all('" + filename + ".json', {useTypes:true})"

    asyncio.run(do_query(cql))


def delete_all() -> None:
    """

    Remove all nodes and relationships in database.

    """

    cql = "MATCH (n) DETACH DELETE n"

    asyncio.run(do_query(cql))
