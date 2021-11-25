"""
API declaration file containing all the endpoints accessible by the program
"""


from fastapi import FastAPI
from downloader.neo4j_driver import get_driver
from neo4j import Driver
from uuid import UUID

app = FastAPI()

@app.get("/query/{query}")
async def query(query):
    driver = get_driver()
    # TODO: Finish this
    return {"result": query}


@app.get("/get_protein/{protein_id}")
async def get_protein(protein_id: UUID):
    driver = get_driver()
    # TODO: Finish this
    return {"result": protein_id}


@app.get("/get_annotation/{annotation_id}")
async def get_annotation(annotation_id: UUID):
    driver = get_driver()
    # TODO: Finish this
    return {"result": annotation_id}


@app.get("/get_entry/{entry_id}")
async def get_entry(entry_id: UUID):
    driver = get_driver()
    # TODO: Finish this
    return {"result": entry_id}


@app.get("/get_neighbors/{neighbors_id}")
async def get_neighbors(neighbors_id: UUID):
    driver = get_driver()
    # TODO: Finish this
    return {"result": neighbors_id}


@app.get("/get_annotated/{annotated_id}")
async def get_annotated(annotated_id: UUID):
    driver = get_driver()
    # TODO: Finish this
    return {"result": annotated_id}
