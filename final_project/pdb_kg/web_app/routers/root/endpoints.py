"""
Root endpoints for the edge service.
"""


from typing import List
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ....data_model import (
    AnnotationResponse,
    EntryResponse,
    NodeBase,
    ProteinResponse,
)
from ....neo4j_driver import get_driver
from ...template_engine import template_environment

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def get_index() -> str:
    """
    Handler for the default path.

    Returns:
        The HTML response.

    """
    template = template_environment.get_template("index.html")
    return await template.render_async()


@router.get("/query/{query}")
async def query(query_text: str) -> List[UUID]:
    driver = get_driver()  # noqa: F841
    # TODO: Finish this
    return {"result": query_text}


@router.get("/get_protein/{protein_id}", response_model=ProteinResponse)
async def get_protein(protein_id: UUID) -> ProteinResponse:
    driver = get_driver()  # noqa: F841
    # TODO: Finish this
    return {"result": protein_id}


@router.get(
    "/get_annotation/{annotation_id}", response_model=AnnotationResponse
)
async def get_annotation(annotation_id: UUID) -> AnnotationResponse:
    driver = get_driver()  # noqa: F841
    # TODO: Finish this
    return {"result": annotation_id}


@router.get("/get_entry/{entry_id}", response_model=EntryResponse)
async def get_entry(entry_id: UUID) -> EntryResponse:
    driver = get_driver()  # noqa: F841
    # TODO: Finish this
    return {"result": entry_id}


@router.get("/get_neighbors/{neighbors_id}")
async def get_neighbors(neighbors_id: UUID) -> List[NodeBase]:
    driver = get_driver()  # noqa: F841
    # TODO: Finish this
    return {"result": neighbors_id}


@router.get("/get_annotated/{annotated_id}")
async def get_annotated(annotated_id: UUID) -> List[UUID]:
    driver = get_driver()  # noqa: F841
    # TODO: Finish this
    return {"result": annotated_id}


@router.get("/get_path", response_model=List[NodeBase])
async def get_path(
    start: UUID, end: UUID, max_length: int = 50
) -> List[NodeBase]:
    """
    Gets the shortest path between a start node and an end node.

    Args:
        start: The UUID of the start node.
        end: The UUID of the end node.
        max_length: The maximum path length.

    Returns:
        The list of the nodes that make up the path, in order. If
        the path does not exist or is too long, it returns an empty list.

    """
