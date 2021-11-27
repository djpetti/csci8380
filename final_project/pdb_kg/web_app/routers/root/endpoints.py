"""
Root endpoints for the edge service.
"""


from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from uuid import UUID

from ...template_engine import template_environment
from ....neo4j_driver import get_driver
from ....data_model import (
    ProteinResponse,
    AnnotationResponse,
    EntryResponse,
)
from typing import List

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
    driver = get_driver()
    # TODO: Finish this
    return {"result": query_text}


@router.get("/get_protein/{protein_id}")
async def get_protein(protein_id: UUID) -> ProteinResponse:
    driver = get_driver()
    # TODO: Finish this
    return {"result": protein_id}


@router.get("/get_annotation/{annotation_id}")
async def get_annotation(annotation_id: UUID) -> AnnotationResponse:
    driver = get_driver()
    # TODO: Finish this
    return {"result": annotation_id}


@router.get("/get_entry/{entry_id}")
async def get_entry(entry_id: UUID) -> EntryResponse:
    driver = get_driver()
    # TODO: Finish this
    return {"result": entry_id}


@router.get("/get_neighbors/{neighbors_id}")
async def get_neighbors(neighbors_id: UUID) -> List[UUID]:
    driver = get_driver()
    # TODO: Finish this
    return {"result": neighbors_id}


@router.get("/get_annotated/{annotated_id}")
async def get_annotated(annotated_id: UUID) -> List[UUID]:
    driver = get_driver()
    # TODO: Finish this
    return {"result": annotated_id}
