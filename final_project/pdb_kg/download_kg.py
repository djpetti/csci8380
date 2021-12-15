import argparse
import asyncio
from typing import Optional

from loguru import logger

from .data_model import NodeLabel
from .downloader.download_manager import DownloadManager
from .downloader.graph_db import (
    create_index,
    create_relationship,
    delete_all,
    save_kg_to_json,
    update_node,
)


async def _create_standard_indices() -> None:
    """
    Creates commonly-used indices.

    """
    await create_index(label=NodeLabel.PROTEIN, properties=("entry_id", "id"))
    await create_index(
        label=NodeLabel.HOST_ORGANISM, properties=("scientific_name",)
    )
    await create_index(
        label=NodeLabel.SOURCE_ORGANISM, properties=("scientific_name",)
    )
    await create_index(
        label=NodeLabel.DATABASE, properties=("reference_database_accession",)
    )
    await create_index(label=NodeLabel.ANNOTATION, properties=("id",))
    await create_index(label=NodeLabel.DRUG, properties=("id",))


async def form_kg(start_at_entry: Optional[str] = None) -> None:
    """
    Create Neo4J database by adding nodes and relationships.

    Args:
        start_at_entry: Start at this particular entry instead of the
            beginning.

    """
    download_manager = DownloadManager()
    # Keeps track of nodes that we've already added.
    added_host_organisms = set()
    added_source_organisms = set()
    added_dbs = set()
    added_annotations = set()
    added_drugs = set()

    async for entry in download_manager.download_entries(
        start_at=start_at_entry
    ):
        await update_node(entry)

        # get each protein which belongs to a specific entry
        async for prot_entity in download_manager.download_entities(entry):
            (
                prot_node,
                host_organ_node,
                source_organ_node,
                db_node,
                anno_node,
            ) = prot_entity
            await update_node(prot_node, key=("entry_id", "id"))
            await create_relationship(entry, prot_node, "HAS_PROTEIN")

            # get Rcsb Entity Host Organism
            for ho in host_organ_node:
                if ho.scientific_name not in added_host_organisms:
                    await update_node(ho, key="scientific_name")
                    await create_relationship(prot_node, ho, "HOST_ON")
                    added_host_organisms.add(ho.scientific_name)

            # get Rcsb Entity Source Organism
            for so in source_organ_node:
                if so.scientific_name not in added_source_organisms:
                    await update_node(so, key="scientific_name")
                    await create_relationship(prot_node, so, "SOURCE_FROM")
                    added_source_organisms.add(so.scientific_name)

            # get Database
            for db in db_node:
                if db.reference_database_accession not in added_dbs:
                    await update_node(db, key="reference_database_accession")
                    await create_relationship(prot_node, db, "REFER_TO")
                    added_dbs.add(db.reference_database_accession)

            # get Annotation
            for anno in anno_node:
                if anno.id not in added_annotations:
                    await update_node(anno, key="id")
                    await create_relationship(
                        prot_node, anno, "HAS_ANNOTATION"
                    )
                    added_annotations.add(anno.id)

            # get Drug and Drug Target
            async for drug, targets in download_manager.download_cofactors(
                prot_node, exclude=added_drugs
            ):
                await update_node(drug, key="id")
                await create_relationship(prot_node, drug, "HAS_COFACTOR")
                for drug_tar in targets:
                    await update_node(drug_tar)
                    await create_relationship(drug, drug_tar, "TARGET_TO")

            added_drugs.update(prot_node.cofactors)


def _make_parser() -> argparse.ArgumentParser:
    """
    Returns:
        The parser to use for parsing CLI arguments.

    """
    parser = argparse.ArgumentParser(
        description="Downloads PDB data and stores them in` Neo4J."
    )

    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="Clear the DB before downloading new stuff.",
    )
    parser.add_argument(
        "-s",
        "--start-from",
        default=None,
        help="Start from this entry ID instead of the beginning.",
    )

    return parser


def main():
    cli_args = _make_parser().parse_args()

    if cli_args.clear:
        logger.info("Clearing the database...")
        delete_all()

    asyncio.run(_create_standard_indices())
    asyncio.run(form_kg(start_at_entry=cli_args.start_from))
    save_kg_to_json("all")


if __name__ == "__main__":
    main()
