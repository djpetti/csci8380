import asyncio
from pdb_kg.downloader.data_model import *
from pdb_kg.downloader import graph_db


def create_relationship(e1: object, e2: object, relation: str):
    """
    Create a relationship between two existed nodes(entities) by using Neo4J query sentence.

    Args:
        e1: Entity 1.
        e2: Entity 2.
        relation: Relation name.

    """

    cql = "MATCH (a:" + e1.label.name + "), (b:" + e2.label.name + ") " \
          "WHERE a.uuid = '" + str(e1.uuid) + "' AND b.uuid = '" + str(e2.uuid) + "' " \
          "CREATE (a)-[:" + relation + "]->(b)"

    asyncio.run(graph_db.do_query(cql))


def form_kg() -> None:
    """
    Create Neo4J database by adding nodes and relationships.

    Returns: None

    """

    prot_node = ProteinNode(id="prot_id", name="prot_name", entry_id="test", entry_name="test_node",
                            sequence="abcdefgzqi",
                            annotations=["abc", "def"], cofactors=["here is", "cofactors test case"])
    asyncio.run(graph_db.update_entry(prot_node))
    """
    Create protein.
    """

    host_node = RcsbEntityHostOrganism(common_names=["common_names"], parent_scientific_name="parent_scientific_name",
                                       scientific_name="scientific_name", taxonomy_id=1,
                                       provenance_source="provenance_source")
    asyncio.run(graph_db.update_entry(host_node))
    """
    Create protein's host organism.
    """

    source_node = RcsbEntitySourceOrganism(common_names=["common_names"],
                                           parent_scientific_name="parent_scientific_name",
                                           scientific_name="scientific_name", taxonomy_id=1,
                                           provenance_source="provenance_source", source_type="gene")
    asyncio.run(graph_db.update_entry(source_node))
    """
    Create protein's source organism.
    """

    drug_node = DrugNode(id="drug_id", name="drug_name", drug_groups=["drug_groups"],
                         drugbank_id="DB123", drugbank_name="drugbank_name", synonyms=["synonyms"])
    asyncio.run(graph_db.update_entry(drug_node))
    """
    Create drug.
    """

    drug_tar_node = DrugbankTarget(interaction_type="interaction_type", name="name", ordinal=1,
                                   organism_common_name="organism_common_name", seq_one_letter_code="seq_one_letter_code")
    asyncio.run(graph_db.update_entry(drug_tar_node))
    """
    Create drug's target.
    """

    db_node = Database(reference_database_accession="P0123", reference_database_name="UniProt")
    asyncio.run(graph_db.update_entry(db_node))
    """
    Create database.
    """

    create_relationship(host_node, prot_node, "HOST_OF")
    create_relationship(source_node, prot_node, "SOURCE_OF")
    create_relationship(prot_node, drug_node, "IS_COMPONENT")
    create_relationship(drug_tar_node, drug_node, "TARGET_OF")
    create_relationship(db_node, prot_node, "FIND_IN")
    create_relationship(db_node, drug_node, "FIND_IN")


def save_kg_to_json(filename: str) -> None:
    """
    Export data in Neo4J into a JSON format file.

    Args:
        filename: Give a string type file name.

    """

    cql = "CALL apoc.export.json.all('" + filename + ".json', {useTypes:true})"

    asyncio.run(graph_db.do_query(cql))


def delete_all() -> None:
    """

    Remove all nodes and relationships in database.

    """

    cql = "MATCH (n) DETACH DELETE n"

    asyncio.run(graph_db.do_query(cql))


def main():
    delete_all()
    form_kg()
    save_kg_to_json("all")


if __name__ == '__main__':
    main()
