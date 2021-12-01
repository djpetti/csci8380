"""
Encapsulates functionality for downloading specific data from PDB.
"""


from typing import List
from urllib.parse import urljoin

from loguru import logger

from aiohttp_session import get_session
from data_model import EntryNode, ProteinNode, Publication

_API_ENDPOINT = "https://data.rcsb.org/rest/v1/"
"""
The main API endpoint for PDB.
"""


async def get_entry_list() -> List[str]:
    """
    Gets the list of entry IDs for all PDB entries. This must be scheduled as
    a task.

    Returns:
        The list of entry IDs.

    """
    entries_url = urljoin(_API_ENDPOINT, "holdings/current/entry_ids")
    logger.debug("Performing GET request to {}.", entries_url)

    session = await get_session()
    async with session.get(entries_url) as response:
        return await response.json()


async def get_entry(entry_id: str) -> EntryNode:
    """
    Gets the information for a particular PDB entry.

    Args:
        entry_id: The unique ID of the entry.

    Returns:
        The entry information.

    """
    entry_url = urljoin(_API_ENDPOINT, f"core/entry/{entry_id}")
    logger.debug("Performing GET request to {}.", entry_url)

    session = await get_session()
    async with session.get(entry_url) as response:
        entry_json = await response.json()

    # Extract citations.
    citations_json = entry_json.get("citation", [])
    citations = []
    for citation in citations_json:
        title = citation.get("title")
        authors = citation.get("authors")
        if title is None or authors is None:
            # Some citations don't have a title or authors; these aren't
            # especially useful.
            continue

        citations.append(
            Publication(
                title=title,
                authors=authors,
                year=citation.get("year"),
            )
        )

    # Extract other info.
    container_ids = entry_json["rcsb_entry_container_identifiers"]
    return EntryNode(
        entry_id=entry_id,
        protein_entity_ids=container_ids.get("polymer_entity_ids", []),
        publications=citations,
    )


async def get_protein_entity(*, entry_id: str, entity_id: str) -> ProteinNode:
    """
    Gets information for a specific protein by entity ID.

    Args:
        entry_id: The ID of the entry that this entity belongs to.
        entity_id: The ID of the entity.

    Returns:
        The protein information.

    """
    entity_url = urljoin(
        _API_ENDPOINT, f"core/polymer_entity/{entry_id}/" f"{entity_id}"
    )
    logger.debug("Performing GET request to {}.", entity_url)

    session = await get_session()
    async with session.get(entity_url) as response:
        entity_json = await response.json()

    # Extract the relevant information.
    poly_info = entity_json["entity_poly"]
    poly_metadata = entity_json["rcsb_polymer_entity"]
    annotations = entity_json.get("rcsb_polymer_entity_annotation", [])
    cofactors = entity_json.get("rcsb_target_cofactors", [])

    # Filter the annotations to GO.
    go_ids = []
    for annotation in annotations:
        annotation_id = annotation["annotation_id"]
        if annotation_id.startswith("GO:"):
            # This is a GO annotation.
            go_ids.append(annotation_id)

    # Extract cofactor IDs.
    cofactor_ids = [c["cofactor_resource_id"] for c in cofactors]

    return ProteinNode(
        entry_id=entry_id,
        id=entity_id,
        name=poly_metadata["pdbx_description"],
        sequence=poly_info["pdbx_seq_one_letter_code_can"],
        annotations=go_ids,
        cofactors=cofactor_ids,
    )
