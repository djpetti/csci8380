import asyncio

from .downloader.download_manager import DownloadManager
from .downloader.graph_db import (
    create_relationship,
    delete_all,
    save_kg_to_json,
    update_node,
)


async def form_kg() -> None:
    """
    Create Neo4J database by adding nodes and relationships.

    Returns: None

    """
    download_manager = DownloadManager()
    # Keeps track of nodes that we've already added.
    added_host_organisms = set()
    added_source_organisms = set()
    added_dbs = set()
    added_annotations = set()
    added_drugs = set()

    async for entry in download_manager.download_entries():
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
            await update_node(prot_node)
            await create_relationship(entry, prot_node, "HAS_PROTEIN")

            # get Rcsb Entity Host Organism
            for ho in host_organ_node:
                if ho.scientific_name not in added_host_organisms:
                    await update_node(ho)
                    await create_relationship(prot_node, ho, "HOST_ON")
                    added_host_organisms.add(ho.scientific_name)

            # get Rcsb Entity Source Organism
            for so in source_organ_node:
                if so.scientific_name not in added_source_organisms:
                    await update_node(so)
                    await create_relationship(prot_node, so, "SOURCE_FROM")
                    added_source_organisms.add(so.scientific_name)

            # get Database
            for db in db_node:
                if db.reference_database_accession not in added_dbs:
                    await update_node(db)
                    await create_relationship(prot_node, db, "REFER_TO")
                    added_dbs.add(db.reference_database_accession)

            # get Annotation
            for anno in anno_node:
                if anno.id not in added_annotations:
                    await update_node(anno)
                    await create_relationship(
                        prot_node, anno, "HAS_ANNOTATION"
                    )
                    added_annotations.add(anno.id)

            # get Drug and Drug Target
            async for drug, targets in download_manager.download_cofactors(
                prot_node, exclude=added_drugs
            ):
                await update_node(drug)
                await create_relationship(prot_node, drug, "HAS_COFACTOR")
                for drug_tar in targets:
                    await update_node(drug_tar)
                    await create_relationship(drug, drug_tar, "TARGET_TO")

                added_drugs.update(prot_node.cofactors)


def main():
    delete_all()
    asyncio.run(form_kg())
    save_kg_to_json("all")


if __name__ == "__main__":
    main()
