"""
API declaration file containing all the endpoints accessible by the program
"""

import asyncio
from fastapi import FastAPI
from downloader.neo4j_driver import get_driver
from downloader.graph_db import get_annotation, get_entry
from uuid import UUID

from loguru import logger

app = FastAPI()


@app.get("/query/{query}")
async def query(query):
    return {"result": query}


@app.get("/get_protein/{protein_id}")
async def get_protein_request(protein_id: UUID):
    return {"result": protein_id}


@app.get("/get_annotation/{annotation_id}")
async def get_annotation_request(annotation_id: UUID):
    logger.debug("Retrieving annotation for id {}".format(annotation_id))
    annotation = await get_annotation(annotation_id)
    return {"result": str(annotation)}


@app.get("/get_entry/{entry_id}")
async def get_entry_request(entry_id: UUID):
    entry = await get_entry(entry_id)
    return {"result": entry}


@app.get("/get_neighbors/{neighbors_id}")
async def get_neighbors_request(neighbors_id: UUID):
    return {"result": neighbors_id}


@app.get("/get_annotated/{annotated_id}")
async def get_annotated_request(annotated_id: UUID):
    return {"result": annotated_id}
