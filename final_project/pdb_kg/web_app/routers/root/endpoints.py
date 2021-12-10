"""
Root endpoints for the edge service.
"""


from typing import List
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from loguru import logger

from ....data_model import (
    AnnotationResponse,
    EntryResponse,
    NodeBase,
    ProteinResponse,
)
from ....downloader.graph_db import (
    get_annotated,
    get_annotation,
    get_entry_2,
    get_neighbors,
    get_path,
    get_protein,
    get_query,
)
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


@router.get("/query/{query_text}")
async def query(query_text: str) -> List[UUID]:
    res = await get_query(query_text)
    return res


@router.get("/get_protein/{protein_id}", response_model=ProteinResponse)
async def get_protein_request(protein_id: UUID) -> ProteinResponse:
    protein = await get_protein(protein_id)
    return protein


@router.get(
    "/get_annotation/{annotation_id}", response_model=AnnotationResponse
)
async def get_annotation_request(annotation_id: UUID) -> AnnotationResponse:
    logger.debug("Retrieving annotation for id {}".format(annotation_id))
    annotation = await get_annotation(annotation_id)
    return annotation


@router.get("/get_entry/{entry_id}", response_model=EntryResponse)
async def get_entry(entry_id: UUID) -> EntryResponse:
    entry = await get_entry_2(entry_id)
    return entry


@router.get("/get_neighbors/{object_id}")
async def get_neighbors_request(object_id: UUID) -> List[NodeBase]:
    nodes = await get_neighbors(object_id)
    return nodes


@router.get("/get_annotated/{annotation_id}")
async def get_annotated_request(annotation_id: UUID) -> List[UUID]:
    nodes = await get_annotated(annotation_id)
    return [n.uuid for n in nodes]


@router.get("/get_path", response_model=List[NodeBase])
async def get_path_request(
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
    path = await get_path(start, end, max_length)
    return path
