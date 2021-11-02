"""
Contains the data model used by this application.
"""


import enum
from typing import Set, List

from pydantic import BaseModel


@enum.unique
class Label(enum.IntEnum):
    """
    Represents labels that nodes can have in the database.
    """

    NONE = enum.auto()
    """
    Specifies that no specific label should be used.
    """
    PROTEIN = enum.auto()
    """
    Indicates that a node represents a protein.
    """
    DRUG = enum.auto()
    """
    Indicates that a node represents a drug.
    """


class NodeMixin:
    """
    Mixin class that allows us to define the model for a node in Neo4J.
    """

    LABEL = Label.NONE
    """
    Node label.
    """


class Entity(BaseModel):
    """
    Common basic entity class for all data sources.

    Attributes:
        id: The unique ID of this entity.
        name: Common human-readable name or description of the entity.

    """

    id: str
    name: str


class ProteinCommon(Entity):
    """
    Common fields for all representations of a protein.

    Attributes:
        sequence: The sequence of the protein, in FASTA notation.

        annotations: Gene ontology annotations that are associated with this
            protein. They should be labeled by the GO ID.
        cofactors: Resource IDs of all associated cofactors for this protein.

    """

    sequence: str

    annotations: Set[str]
    cofactors: Set[str]


class ProteinNode(ProteinCommon, NodeMixin):
    """
    A node representing a protein in the graph database.
    """

    LABEL = Label.PROTEIN


class DrugGroup(Entity):
    """
    Common fields for all representations of a drug.

    Attributes:
        drug_groups: Represents the drug groups that this entity belongs to.

    """

    drug_groups: Set[str]


class DrugbankInfo(DrugGroup, NodeMixin):
    """
    A node representing a drug in the graph database.
    """

    LABEL = Label.DRUG

    drugbank_id: str
    name: str
    synonyms: Set[str]


class DrugbankTarget:
    """
    A node representing interaction type and information of a drug.
    """

    name: str
    interaction_type: str
    ordinal: int
    organism_common_name: str
    seq_one_letter_code: str
    reference_database_accession_code: str


class Database:
    """
    A node representing which database can find the drug's components.
    """

    name: str


class RcsbClusterMembership:
    """

    """

    cluster_id: int
    identity: int


class EntityPoly:
    """

    """

    nstd_linkage: str
    nstd_monomer: str
    pdbx_seq_one_letter_code: str
    pdbx_seq_one_letter_code_can: str
    pdbx_strand_id: str
    rcsb_artifact_monomer_count: int
    rcsb_conflict_count: int
    rcsb_deletion_count: int
    rcsb_entity_polymer_type: str
    rcsb_insertion_count: int
    rcsb_mutation_count: int
    rcsb_non_std_monomer_count: int
    rcsb_sample_sequence_length: int
    type: str


class EntitySrcGen:
    """

    """

    gene_src_common_name: str
    gene_src_genus: str
    host_org_genus: str
    pdbx_alt_source_flag: str
    pdbx_gene_src_gene: str
    pdbx_gene_src_ncbi_taxonomy_id: str
    pdbx_gene_src_scientific_name: str
    pdbx_host_org_ncbi_taxonomy_id: str
    pdbx_host_org_scientific_name: str
    pdbx_src_id: int


class RcsbEntityHostOrganism:
    """

    """

    ncbi_common_names: Set[str]
    ncbi_parent_scientific_name: str
    ncbi_scientific_name: str
    ncbi_taxonomy_id: int
    pdbx_src_id: str
    provenance_source: str
    scientific_name: str


class TaxonomyLineageOfRcsbEntityHostOrganism(RcsbEntityHostOrganism):
    """

    """

    depth: int
    id: str
    name: str


class RcsbEntitySourceOrganism:
    """

    """

    common_name: str
    ncbi_common_names: Set[str]
    ncbi_parent_scientific_name: str
    ncbi_scientific_name: str
    ncbi_taxonomy_id: int
    pdbx_src_id: str
    provenance_source: str
    scientific_name: str
    source_type: str


class TaxonomyLineageOfRcsbEntitySourceOrganism(RcsbEntitySourceOrganism):
    """

    """

    depth: int
    id: str
    name: str


class RcsbGeneNameOfRcsbEntitySourceOrganism(RcsbEntitySourceOrganism):
    """

    """

    provenance_source: str
    value: str


class RcsbPolymerEntity:
    """

    """

    formula_weight: float
    pdbx_description: str
    pdbx_number_of_molecules: int
    rcsb_multiple_source_flag: str
    rcsb_source_part_count: int
    rcsb_source_taxonomy_count: int
    src_method: str


class RcsbMacromolecularNamesCombinedOfRcsbPolymerEntity(RcsbPolymerEntity):
    """

    """

    name: str
    provenance_code: str
    provenance_source: str


class RcsbPolymerEntityAlign:
    """

    """

    provenance_source: str
    reference_database_accession: str
    reference_database_name: str


class AlignedRegionsOfRcsbPolymerEntityAlign(RcsbPolymerEntityAlign):
    """

    """

    entity_beg_seq_id: int
    length: int
    ref_beg_seq_id: int


class RcsbPolymerEntityAnnotation:
    """

    """

    annotation_id: str
    assignment_version: str
    name: str
    provenance_source: str
    type: str


class AnnotationLineageOfRcsbPolymerEntityAnnotation(RcsbPolymerEntityAnnotation):
    """

    """

    id: str
    name: str


class RcsbPolymerEntityContainerIdentifiers:
    """

    """

    asym_ids: Set[str]
    auth_asym_ids: Set[str]
    chem_comp_monomers: Set[str]
    entity_id: str
    entry_id: str
    rcsb_id: str
    uniprot_ids: Set[str]


class ReferenceSequenceIdentifiersOfRcsbPolymerEntityContainerIdentifiers(RcsbPolymerEntityContainerIdentifiers):
    """

    """

    database_accession: str
    database_name: str
    provenance_source: str


class RcsbPolymerEntityFeature:
    """

    """

    assignment_version: str
    feature_id: str
    name: str
    provenance_source: str
    type: str


class FeaturePositionsOfRcsbPolymerEntityFeature(RcsbPolymerEntityFeature):
    """

    """

    beg_seq_id: int
    end_seq_id: int
    values: List[float]


class RcsbPolymerEntityFeatureSummary:
    """

    """
    count: int
    coverage: float
    type: str


class RcsbRelatedTargetReferences:
    """

    """
    related_resource_name: str
    related_resource_version: int
    related_target_id: str
    target_taxonomy_id: int


class AlignedTargetOfRcsbRelatedTargetReferences(RcsbRelatedTargetReferences):
    """

    """

    entity_beg_seq_id: int
    length: int
    target_beg_seq_id: int


class RcsbTargetCofactors:
    """

    """

    cofactor_name: str
    cofactor_resource_id: str
    mechanism_of_action: str
    neighbor_flag: str
    pubmed_ids: Set[int]
    resource_name: str
    resource_version: str
    target_resource_id: str
    cofactor_in_ch_ikey: str
    cofactor_smiles: str
    cofactor_chem_comp_id: str


class RcsbId:
    """

    """

    rcsb_id: str


class RcsbGenomicLineage:
    """

    """

    id: str
    name: str
    depth: int


class RcsbClusterFlexibility:
    """

    """

    link: str
    label: str
    avg_rmsd: float
    max_rmsd: float
    provenance_code: str


class RcsbLatestRevision:
    """

    """

    major_revision: int
    minor_revision: int
