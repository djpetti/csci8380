"""
Contains low-level functions for interfacing with the graph database.
"""
import asyncio
import re
from functools import singledispatch
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from uuid import UUID

from loguru import logger
from neo4j import Result, Transaction
from pydantic.error_wrappers import ValidationError

from ..data_model import (
    AnnotationResponse,
    EntryNode,
    EntryResponse,
    NodeBase,
    NodeLabel,
    ProteinNode,
    ProteinResponse,
)
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
    # Remove quotes in the string.
    value = value.replace('"', "")
    return f'"{value}"'


@_to_cypher.register
def _(value: int) -> str:
    return _to_cypher(str(value))


@_to_cypher.register(type(None))
def _(value: type(None)) -> str:
    return "null"


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


@_to_cypher.register(dict)
def _(value: Dict[str, Any], convert_values: bool = True) -> str:
    """
    Args:
        value: The dictionary to convert.
        convert_values: Whether to also convert the dictionary values.
            Otherwise, they will be left the way they are.

    Returns:
        The corresponding cypher mapping.

    """
    # Create the mapping.
    if convert_values:
        cypher_attributes = {k: _to_cypher(v) for k, v in value.items()}
    else:
        cypher_attributes = value

    cypher_pairs = [": ".join(item) for item in cypher_attributes.items()]
    mapping_items = ", ".join(cypher_pairs)
    return f"{{{mapping_items}}}"


@_to_cypher.register
def _(
    value: NodeBase,
    exclude_properties: Iterable[str] = ("uuid",),
    include_properties: Optional[Iterable[str]] = None,
) -> str:
    """
    Args:
        value: The node to convert.
        exclude_properties: Properties to exclude when serializing the
            structure. By default, it excludes the UUID.
        include_properties: Properties to include when serializing the
            structure. If provided, only these properties will be included.

    Returns:
        The Cypher mapping corresponding to this node structure.

    """
    exclude_set = {"label"}
    exclude_set.update(exclude_properties)
    if include_properties:
        node_attributes = value.dict(include=frozenset(include_properties))
    else:
        node_attributes = value.dict(exclude=exclude_set)

    # Create the mapping.
    return _to_cypher(node_attributes)


def _update_entry_transaction(
    transaction: Transaction,
    entry: EntryNode,
    key: Iterable[str] = ("uuid",),
) -> None:
    """
    Transaction function that updates (or creates) an entry node.

    Args:
        transaction: The transaction object.
        entry: The entry information.
        key: The name of the attribute(s) to use as a key to determine whether
            the node exists or not. By default, it uses the UUID.

    """
    # Generate the key portion of the query and the substitutions.
    key_dict = {}
    key_substitutions = {}
    for index, attribute in enumerate(key):
        placeholder = f"key_{index}"
        key_dict[attribute] = f"${placeholder}"
        key_substitutions[placeholder] = _to_cypher(getattr(entry, attribute))

    query = (
        f"MERGE (entry:{entry.label.name} "
        f"{_to_cypher(key_dict, convert_values=False)}) SET "
        f"entry += {_to_cypher(entry, exclude_properties=(key,))}"
    )
    logger.debug("Running query: {}", query)

    transaction.run(
        query,
        **key_substitutions,
    )


def _create_index_transaction(
    transaction: Transaction, *, label: NodeLabel, properties: Iterable[str]
) -> None:
    """
    Transaction function that creates a new index, if it does not already
    exist.

    Args:
        transaction: The transaction object.
        label: The label for the node type we are indexing.
        properties: The names of the properties to use to create the index.

    """
    logger.debug(
        "Creating an index for {} on properties {}.", label.name, properties
    )

    # Generate the properties tuple.
    properties_str = [f"node.{p}" for p in properties]
    properties_str = ", ".join(properties_str)

    transaction.run(
        f"CREATE INDEX IF NOT EXISTS FOR "
        f"(node:{label.name}) ON ({properties_str})"
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


def run_read_query(query: str):
    """
    Runs a query with a simple read request. This function helps to remove
    boilerplate.

    Args:
        query: The query to be run.
    """

    def _rt(transaction: Transaction, ts: str):
        logger.debug(f"Running transaction {query}")
        res = transaction.run(ts)
        return list(res.graph().nodes)

    return fetch_read(_rt, query)


def simple_get_transaction(label, uuid: UUID):
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


async def update_node(
    entry: NodeBase, key: Union[str, Iterable[str]] = "uuid"
) -> None:
    """
    Updates or creates a particular node.

    Notes:
        The synchronous database access is performed in a separate thread.

    Args:
        entry: The entry information.
        key: The name of the attribute to use as a key to determine whether
            the node exists or not. By default, it uses the UUID.

    """
    # Normalize the key.
    if isinstance(key, str):
        key = (key,)

    def _update_entry_sync(_entry: EntryNode) -> None:
        with get_driver().session() as session:
            session.write_transaction(
                _update_entry_transaction, _entry, key=key
            )

    await run_in_thread(_update_entry_sync, entry)


async def create_index(*, label: NodeLabel, properties: Iterable[str]) -> None:
    """
    Create a new index, if it does not already exist.

    Args:
        label: The label for the node type we are indexing.
        properties: The names of the properties to use to create the index.

    """

    def _create_index_sync(
        _label: NodeLabel, _properties: Iterable[str]
    ) -> None:
        with get_driver().session() as session:
            session.write_transaction(
                _create_index_transaction, label=_label, properties=_properties
            )

    await run_in_thread(_create_index_sync, label, properties)


def is_pdb_entry_id(string: str) -> bool:
    """
    Determines if the given string is a valid pdb entry id as defined by
    https://proteopedia.org/wiki/index.php/PDB_code

    Args:
        string: The string to check if is a valid pdb entry id

    Returns:
        True if the string constitutes a single pdb entry id, false otherwise
    """
    return bool(re.match(r"^[1-9][a-zA-Z0-9]{3}$", string))


async def get_pdb_entry_by_name(string: str) -> List[UUID]:
    """
    Fetches a list of pdb entries that match the given entry id.

    Args:
        string: The entry id for the proteins

    Returns:
        A list of UUIDs corresponding to retrieved pdb entries
    """
    query = f"MATCH (p:PROTEIN {{entry_id: '{string}'}}) RETURN p"
    query_res = await run_in_thread(run_read_query, query)
    query_res = [x.get("uuid") for x in query_res]
    return query_res


def is_go_id(string: str) -> bool:
    """
    Determines if the given string is a valid GO id based on whether it starts
    with 'GO:'

    Args:
        string: The string to check if is a GO id

    Returns:
        True if the string constitutes a single GO id, false otherwise
    """
    return bool(re.match(r"^GO:", string))


async def get_go_id_by_name(string: str) -> List[UUID]:
    """
    Fetches a list of pdb entries that match the given entry id.

    Args:
        string: The entry id for the proteins

    Returns:
        A list of UUIDs corresponding to retrieved pdb entries
    """
    query = (
        f"MATCH (p:PROTEIN)-[:HAS_ANNOTATION]-"
        f"(g:ANNOTATION {{id: '{string}'}}) RETURN p"
    )
    query_res = await run_in_thread(run_read_query, query)
    query_res = [x.get("uuid") for x in query_res]
    return query_res


def is_fasta_sequence(string: str) -> bool:
    """
    Determines if a given string is a FASTA sequence by checking if the string
    contains all uppercase letters. There is more than likely a more
    comprehensive way to find this out, but most the methods I found involve a
    much more complicated process. I can work on this more if that is
    important.

    Args:
        string: String to determine if is a fasta sequence

    Returns:
        True if the string is considered a valid sequence, false otherwise
    """
    return string.isalpha() and string.isupper()


async def get_proteins_by_seq(seq: str) -> List[UUID]:
    """
    Retrieves a list of proteins which contain a subsequence or match the
    sequence given.

    Args:
        seq: The subseq/seq to fuzzy search for

    Returns:
        A list of UUIDs for proteins which match the seq
    """
    query = f"MATCH (g:PROTEIN) WHERE g.seq CONTAINS '{seq}' RETURN g"
    query_res = await run_in_thread(run_read_query, query)
    query_res = [x.get("uuid") for x in query_res]
    return query_res


async def get_fuzzy_entries(string: str) -> List[UUID]:
    """
    Fallback protocol for the querying function. Runs a fuzzy search to find
    all the elements where either the protein or annotation contains the given
    string as part of their id.

    Args:
        string: The string which an id may contain

    Returns:
        All proteins and annotations which contain this string in their id
    """
    query = (
        f"MATCH(g:PROTEIN) WHERE g.name CONTAINS '{string}' RETURN g LIMIT 25"
    )
    query_res = await run_in_thread(run_read_query, query)
    query_res = [x.get("uuid") for x in query_res]
    return query_res


async def get_query(query_string: str) -> List[UUID]:
    """
    Gets the results for a search query given a query_string. This can fall
    under a few options, with them being prioritized in the order they are
    listed:
    1. If the query is a valid PDB entry ID, e.g. “4HHB”, it should return all
    proteins associated with that entry.
    2. If the query is a valid GO ID, e.g.  “GO:0005623”, it should return all
    proteins with that annotation.
    3. If the query is a valid FASTA sequence, it should fuzzy-match to
    proteins with similar sequences.
    4. For anything else, it should fuzzy-match to the protein names or the GO
    node descriptions, and respond with any related proteins.

    Args:
        query_string: The query string to be parsed and find the results for

    Returns:
        Results corresponding to what the query string is most likely referring
        to
    """
    logger.debug("Got query: {}", query_string)
    if is_pdb_entry_id(query_string):
        res = await get_pdb_entry_by_name(query_string)
    elif is_go_id(query_string):
        res = await get_go_id_by_name(query_string)
    elif is_fasta_sequence(query_string):
        res = await get_proteins_by_seq(query_string)
    else:
        res = await get_fuzzy_entries(query_string)
    return res


async def get_entry_2(entry_uuid: UUID) -> EntryResponse:
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

    query = (
        f'MATCH (e:ENTRY {{uuid: "{entry_uuid}"}})'
        f"-[:HAS_PROTEIN]-(p) RETURN p"
    )
    protein_info = await run_in_thread(run_read_query, query)
    protein_info = [x.get("uuid") for x in protein_info]
    return EntryResponse(**node_info[0], protein_entity_uuids=protein_info)


async def get_annotation(annotation_id: UUID) -> AnnotationResponse:
    """
    Fetches an annotation by its UUID.

    Args:
        annotation_id: The UUID of the annotation.

    Returns:
        An AnnotationNode with the desired UUID if found.

    """
    node_info = await run_in_thread(
        simple_get_transaction, NodeLabel.ANNOTATION, annotation_id
    )
    # Convert to an EntryNode structure.
    return AnnotationResponse(**node_info[0])


async def get_protein(protein_id: UUID) -> ProteinResponse:
    """
    Fetches a protein by its UUID.

    Args:
        protein_id: The UUID of the protein.

    Returns:
        An AnnotationNode with the desired UUID if found.

    """
    node_info = await run_in_thread(
        simple_get_transaction, NodeLabel.PROTEIN, protein_id
    )

    entry_query = (
        f"MATCH (e:ENTRY)-[:HAS_PROTEIN]-"
        f"(p:PROTEIN {{uuid: '{protein_id}'}}) RETURN e"
    )
    entry_info = await run_in_thread(run_read_query, entry_query)
    if len(entry_info) < 1:
        # No entry, often resulting from an incomplete database.
        logger.warning(
            "No entry data for protein {}. Is the DB complete?", protein_id
        )
        entry_uuid = None
    else:
        entry_uuid = entry_info[0].get("uuid")

    annotation_query = (
        f"MATCH (p:PROTEIN {{uuid: '{protein_id}'}})-[:HAS_ANNOTATION]-"
        f"(a:ANNOTATION) RETURN a"
    )
    annotation_info = await run_in_thread(run_read_query, annotation_query)
    annotation_info = [x.get("uuid") for x in annotation_info]

    cofactor_query = (
        f"MATCH (p:PROTEIN {{uuid: '{protein_id}'}})-[:HAS_COFACTOR]-"
        f"(c) RETURN c"
    )
    cofactor_info = await run_in_thread(run_read_query, cofactor_query)
    cofactor_info = [x.get("uuid") for x in cofactor_info]

    return ProteinResponse(
        **node_info[0],
        entry_uuid=entry_uuid,
        annotation_uuids=set(annotation_info),
        cofactor_uuids=set(cofactor_info),
    )


def convert_node(node_info):
    """
    Given a Node fetched from Neo4j, parses the label retrieved and converts
    the node into the pydantic version defined by our data_model.

    Args:
        node_info: Information for the node retrieved from the Neo4j graph

    Returns:
        Node corresponding to the type of node defined by the label.

    """

    (node_type,) = node_info.labels
    try:
        return NodeBase(label=node_type.lower(), **node_info)
    except ValidationError:
        if node_type == "DRUGBANK_TARGET":
            return NodeBase(label=1, **node_info)
        elif node_type == "DATABASE":
            return NodeBase(label=2, **node_info)
        elif node_type == "HOST_ORGANISM":
            return NodeBase(label=3, **node_info)
        elif node_type == "SOURCE_ORGANISM":
            return NodeBase(label=4, **node_info)


async def get_neighbors(object_id: UUID) -> List[NodeBase]:
    """
    Finds all the neighbors of any object in the Neo4j graph. They all exist at
    a 1 hop from the given object.

    Args:
        object_id: The UUID of the object to find the neighbors for

    Returns:
        List of nodes that are directly connected to the given object. Each of
        the nodes will have its properties fully defined.
    """
    query = f'MATCH ({{uuid: "{object_id}"}})-[*1]-(c) RETURN c'
    node_info = await run_in_thread(run_read_query, query)
    for node in node_info:
        convert_node(node)
    node_info = [convert_node(node) for node in node_info]
    return node_info


async def get_annotated(annotation_id: UUID) -> List[ProteinNode]:
    """
    Finds all the neighbors of an annotation in the Neo4j graph. They all exist
    at a 1 hop from the given annotation.

    Args:
        annotation_id: The UUID of the annotation to find the neighbors for

    Returns:
        List of nodes that are directly connected to the given annotation. Each
        of the nodes will have its properties fully defined.
    """
    query = (
        f'MATCH ({{uuid: "{annotation_id}"}})'
        f"-[*1]-(c:{NodeLabel.PROTEIN.name}) RETURN c"
    )
    node_info = await run_in_thread(run_read_query, query)
    node_info = [ProteinNode(**node) for node in node_info]
    return node_info


async def get_path(start: UUID, end: UUID, max_length: int) -> List[NodeBase]:
    """
    Finds the shortest path between two given objects in the Neo4j graph. If
    the path is not within the max length or if the path does not exist,
    an empty list is returned.

    Args:
        start: The UUID of the object at the start of the path
        end: The UUID of the object at the end of the path
        max_length: The maximum length of the path allowed

    Returns:
        List of nodes in order of which they appear from start to end. If the
        path is not within the max length or if the path does not exist, an
        empty list is returned.
    """
    query = (
        f"MATCH "
        f'(a {{uuid: "{start}"}}), '
        f'(b {{uuid: "{end}"}}), '
        f"p=shortestPath((a)-[*]-(b)) "
        f"WITH p "
        f"WHERE length(p) < {max_length} "
        f"RETURN p"
    )
    node_info = await run_in_thread(run_read_query, query)
    node_info = [convert_node(node) for node in node_info]
    return node_info


async def do_query(cql: str) -> None:
    """
    Run a particular cypher through inputting custom query sentence.

    Args:
        cql: The created query sentence under NEO4J format.

    """

    with get_driver().session() as session:
        session.run(cql)


async def create_relationship(e1: NodeBase, e2: NodeBase, relation: str):
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
