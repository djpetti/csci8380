"""
API declaration file containing all the endpoints accessible by the program
"""

import asyncio
from typing import List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from neo4j_driver import get_driver
from downloader.graph_db import (
        get_annotation, 
        get_entry_2,
        get_protein,
        get_neighbors,
        get_annotated,
        get_path,
)
from uuid import UUID

from data_model import (
        ProteinNode,
        AnnotationNode,
        EntryResponse,
        EntryNode,
        NodeBase,
)

from loguru import logger

app = FastAPI()


@app.get("/query/{query}")
async def query(query):
    return {"result": query}


@app.get("/get_protein/{protein_id}", response_model=ProteinNode)
async def get_protein_request(protein_id: UUID):
    protein = await get_protein(protein_id)
    return protein


@app.get("/get_annotation/{annotation_id}", response_model=AnnotationNode)
async def get_annotation_request(annotation_id: UUID):
    logger.debug("Retrieving annotation for id {}".format(annotation_id))
    annotation = await get_annotation(annotation_id)
    return annotation


@app.get("/get_entry/{entry_id}", response_model=EntryResponse)
async def get_entry_request(entry_id: UUID):
    entry = await get_entry_2(entry_id)
    return entry


@app.get("/get_neighbors/{object_id}", response_model=List[NodeBase])
async def get_neighbors_request(object_id: UUID):
    nodes = await get_neighbors(object_id)
    return nodes


@app.get("/get_annotated/{annotation_id}", response_model=List[ProteinNode])
async def get_annotated_request(annotation_id: UUID):
    nodes = await get_annotated(annotation_id)
    return nodes


@app.get("/get_path/{start}/{end}/{max_length}", response_model=List[NodeBase])
async def get_path_request(start: UUID, end: UUID, max_length: int):
    path = await get_path(start, end, max_length)
    return path
