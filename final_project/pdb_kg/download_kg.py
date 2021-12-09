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

    async for entry in download_manager.download_entries():
        await update_node(entry)

        # get each protein which belongs to a specific entry
        async for prot_entity in download_manager.download_entities(entry):
            prot_list = []
            (
                prot_node,
                host_organ_node,
                source_organ_node,
                db_node,
                anno_node,
                drug_node,
                drug_tar_list_list,
            ) = prot_entity
            await update_node(prot_node)
            await create_relationship(entry, prot_node, "HAS_PROTEIN")

            # get Rcsb Entity Host Organism
            for ho in host_organ_node:
                await update_node(ho)
                await create_relationship(prot_node, ho, "HOST_ON")

            # get Rcsb Entity Source Organism
            for so in source_organ_node:
                await update_node(so)
                await create_relationship(prot_node, so, "SOURCE_FROM")

            # get Database
            for db in db_node:
                await update_node(db)
                await create_relationship(prot_node, db, "REFER_TO")

            # get Annotation
            for anno in anno_node:
                await update_node(anno)
                await create_relationship(prot_node, anno, "HAS_ANNOTATION")

            # get Drug and Drug Target
            for index, drug in enumerate(drug_node):
                await update_node(drug)
                await create_relationship(prot_node, drug, "HAS_COFACTOR")
                for drug_tar in drug_tar_list_list[index]:
                    await update_node(drug_tar)
                    await create_relationship(drug, drug_tar, "TARGET_TO")

            # Create relationship between nodes have similar sequence
            if len(prot_list) > 1:
                for prev_prot in prot_list:
                    await create_relationship(
                        prev_prot, prot_node, "SIMILAR_SEQUENCE"
                    )
                    await create_relationship(
                        prot_node, prev_prot, "SIMILAR_SEQUENCE"
                    )
            prot_list.append(prot_node)


def main():
    delete_all()
    asyncio.run(form_kg())
    save_kg_to_json("all")


if __name__ == "__main__":
    main()
