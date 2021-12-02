"""
API declaration file containing all the endpoints accessible by the program
"""

import asyncio
from fastapi import FastAPI
from neo4j_driver import get_driver
from downloader.graph_db import (
        get_annotation, 
        get_entry,
        get_protein,
        get_neighbors,
        get_annotated,
        get_path,
)
from uuid import UUID

from loguru import logger

app = FastAPI()


@app.get("/query/{query}")
async def query(query):
    return {"result": query}


@app.get("/get_protein/{protein_id}")
async def get_protein_request(protein_id: UUID):
    protein = get_protein(protein_id)
    return {"result": str(protein)}


@app.get("/get_annotation/{annotation_id}")
async def get_annotation_request(annotation_id: UUID):
    logger.debug("Retrieving annotation for id {}".format(annotation_id))
    annotation = await get_annotation(annotation_id)
    return {"result": str(annotation)}


@app.get("/get_entry/{entry_id}")
async def get_entry_request(entry_id: UUID):
    entry = await get_entry(entry_id)
    return {"result": str(entry)}


@app.get("/get_neighbors/{object_id}")
async def get_neighbors_request(object_id: UUID):
    nodes = await get_neighbors(object_id)
    return {"result": str(nodes)}


@app.get("/get_annotated/{annotation_id}")
async def get_annotated_request(annotation_id: UUID):
    nodes = await get_annotated(annotation_id)
    return {"result": str(nodes)}


@app.get("/get_path/{start}/{end}/{max_length}")
async def get_path_request(start: UUID, end: UUID, max_length: int):
    path = await get_path(start, end, max_length)
    return {"result": str(path)}
