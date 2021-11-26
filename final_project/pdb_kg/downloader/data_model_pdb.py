"""
Contains the data model used by this application.
"""


import enum
from typing import List, Optional, Set, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


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
    ENTRY = enum.auto()
    """
    Indicates that a node represents a PDB entry.
    """
    ANNOTATION = enum.auto()
    """
    Indicates that a node represents an ontology annotation.
    """

    DrugbankTarget = enum.auto()
    Database = enum.auto()
    RcsbClusterMembership = enum.auto()
    EntityPoly = enum.auto()
    EntitySrcGen = enum.auto()
    RcsbEntityHostOrganism = enum.auto()
    RcsbEntitySourceOrganism = enum.auto()
    RcsbPolymerEntity = enum.auto()
    RcsbPolymerEntityAlign = enum.auto()
    RcsbPolymerEntityAnnotation = enum.auto()
    RcsbPolymerEntityContainerIdentifiers = enum.auto()
    RcsbPolymerEntityFeature = enum.auto()
    RcsbPolymerEntityFeatureSummary = enum.auto()
    RcsbRelatedTargetReferences = enum.auto()
    RcsbTargetCofactors = enum.auto()
    RcsbId = enum.auto()
    RcsbGenomicLineage = enum.auto()
    RcsbClusterFlexibility = enum.auto()
    RcsbLatestRevision = enum.auto()


class NodeBase(BaseModel):
    """
    Contains attributes shared by all models representing Neo4J nodes.

    Attributes:
        uuid: Unique identifier used by the graph DB to identify this node.
        label: The label of this node.

    """

    uuid: UUID = Field(default_factory=uuid4)
    label: Label


class Publication(BaseModel):
    """
    Represents a publication.

    Attributes:
        title: The title of the publication.
        authors: The full names of the authors of the publication, in order.
        year: The year that this was published.

    """

    title: str
    authors: Tuple[str, ...]
    year: Optional[int]


class EntryNode(NodeBase):
    """
    A node representing a PDB entry in the graph database.

    Attributes:
        entry_id: The corresponding entry ID in PDB.
        protein_entity_ids: The IDs of all the child protein entities under
            this entry.

    """

    label: Label = Label.ENTRY

    entry_id: str
    protein_entity_ids: Set[str]

    publications: Tuple[Publication, ...]


class DrugbankTarget(NodeBase):
    """
    A node representing interaction type and information of a drug.
    """

    label: Label = Label.DrugbankTarget

    name: str
    interaction_type: str
    ordinal: int
    organism_common_name: str
    seq_one_letter_code: str
    reference_database_accession_code: str


class Database(NodeBase):
    """
    A node representing which database can find the drug's components.
    """

    label: Label = Label.Database

    name: str


class RcsbClusterMembership(NodeBase):
    """"""

    label: Label = Label.RcsbClusterMembership

    cluster_id: int
    identity: int


class EntityPoly(NodeBase):
    """"""

    label: Label = Label.EntityPoly

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


class EntitySrcGen(NodeBase):
    """"""

    label: Label = Label.EntitySrcGen

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


class RcsbEntityHostOrganism(NodeBase):
    """"""

    label: Label = Label.RcsbEntityHostOrganism

    ncbi_common_names: Set[str]
    ncbi_parent_scientific_name: str
    ncbi_scientific_name: str
    ncbi_taxonomy_id: int
    pdbx_src_id: str
    provenance_source: str
    scientific_name: str


class TaxonomyLineageOfRcsbEntityHostOrganism(RcsbEntityHostOrganism):
    """"""

    depth: int
    id: str
    name: str


class RcsbEntitySourceOrganism(NodeBase):
    """"""

    label: Label = Label.RcsbEntitySourceOrganism

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
    """"""

    depth: int
    id: str
    name: str


class RcsbGeneNameOfRcsbEntitySourceOrganism(RcsbEntitySourceOrganism):
    """"""

    provenance_source: str
    value: str


class RcsbPolymerEntity(NodeBase):
    """"""

    label: Label = Label.RcsbPolymerEntity

    formula_weight: float
    pdbx_description: str
    pdbx_number_of_molecules: int
    rcsb_multiple_source_flag: str
    rcsb_source_part_count: int
    rcsb_source_taxonomy_count: int
    src_method: str


class RcsbMacromolecularNamesCombinedOfRcsbPolymerEntity(RcsbPolymerEntity):
    """"""

    name: str
    provenance_code: str
    provenance_source: str


class RcsbPolymerEntityAlign(NodeBase):
    """"""

    label: Label = Label.RcsbPolymerEntityAlign

    provenance_source: str
    reference_database_accession: str
    reference_database_name: str


class AlignedRegionsOfRcsbPolymerEntityAlign(RcsbPolymerEntityAlign):
    """"""

    entity_beg_seq_id: int
    length: int
    ref_beg_seq_id: int


class RcsbPolymerEntityAnnotation(NodeBase):
    """"""

    label: Label = Label.RcsbPolymerEntityAnnotation

    annotation_id: str
    assignment_version: str
    name: str
    provenance_source: str
    type: str


class AnnotationLineageOfRcsbPolymerEntityAnnotation(
    RcsbPolymerEntityAnnotation
):
    """"""

    id: str
    name: str


class RcsbPolymerEntityContainerIdentifiers(NodeBase):
    """"""

    label: Label = Label.RcsbPolymerEntityContainerIdentifiers

    asym_ids: Set[str]
    auth_asym_ids: Set[str]
    chem_comp_monomers: Set[str]
    entity_id: str
    entry_id: str
    rcsb_id: str
    uniprot_ids: Set[str]


class ReferenceSequenceIdentifiersOfRcsbPolymerEntityContainerIdentifiers(
    RcsbPolymerEntityContainerIdentifiers
):
    """"""

    database_accession: str
    database_name: str
    provenance_source: str


class RcsbPolymerEntityFeature(NodeBase):
    """"""

    label: Label = Label.RcsbPolymerEntityFeature

    assignment_version: str
    feature_id: str
    name: str
    provenance_source: str
    type: str


class FeaturePositionsOfRcsbPolymerEntityFeature(RcsbPolymerEntityFeature):
    """"""

    beg_seq_id: int
    end_seq_id: int
    values: List[float]


class RcsbPolymerEntityFeatureSummary(NodeBase):
    """"""

    label: Label = Label.RcsbPolymerEntityFeatureSummary

    count: int
    coverage: float
    type: str


class RcsbRelatedTargetReferences(NodeBase):
    """"""

    label: Label = Label.RcsbRelatedTargetReferences

    related_resource_name: str
    related_resource_version: int
    related_target_id: str
    target_taxonomy_id: int


class AlignedTargetOfRcsbRelatedTargetReferences(RcsbRelatedTargetReferences):
    """"""

    entity_beg_seq_id: int
    length: int
    target_beg_seq_id: int


class RcsbTargetCofactors(NodeBase):
    """"""

    label: Label = Label.RcsbTargetCofactors

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


class RcsbId(NodeBase):
    """"""

    label: Label = Label.RcsbId

    rcsb_id: str


class RcsbGenomicLineage(NodeBase):
    """"""

    label: Label = Label.RcsbGenomicLineage

    id: str
    name: str
    depth: int


class RcsbClusterFlexibility(NodeBase):
    """"""

    label: Label = Label.RcsbClusterFlexibility

    link: str
    label: str
    avg_rmsd: float
    max_rmsd: float
    provenance_code: str


class RcsbLatestRevision(NodeBase):
    """"""

    label: Label = Label.RcsbLatestRevision

    major_revision: int
    minor_revision: int
