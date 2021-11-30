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
    DRUGBANKTARGET = enum.auto()
    """
    Indicates that a node represents a drug's target.
    """
    DATABASE = enum.auto()
    """
    Indicates that a node represents a protein database.
    """
    RCSBENTITYHOSTORGANISM = enum.auto()
    """
    Indicates that a node represents a host organism of a protein.
    """
    RCSBENTITYSOURCEORGANISM = enum.auto()
    """
    Indicates that a node represents a source organism of a protein.
    """


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


class Entity(NodeBase):
    """
    Common basic entity class for all data sources.

    Attributes:
        id: The unique ID of this entity.
        name: Common human-readable name or description of the entity.

    """

    id: str
    name: str


class ProteinNode(Entity):
    """
    A node representing a protein in the graph database.

    Attributes:
        entry_id: The ID of the parent PDB entry for this protein.
        name: The name of the parent PDB entry for this protein.

        sequence: The sequence of the protein, in FASTA notation.
        sequence: The length of the protein sequence.

        annotations: Gene ontology annotations that are associated with this
            protein. They should be labeled by the GO ID.
        cofactors: Resource IDs of all associated cofactors for this protein.

    """

    label: Label = Label.PROTEIN

    entry_id: str
    name: str

    sequence: str
    sequence_length: int

    annotations: Set[str]
    cofactors: Set[str]


class RcsbEntityHostOrganism(NodeBase):
    """
    A node representing a host organism of a protein.

    Attributes:
        common_names: Common names from NCBI.
        parent_scientific_name: Parent's scientific name from NCBI.
        scientific_name: Scientific name from NCBI.
        taxonomy_id: Taxonomy ID from NCBI.
        provenance_source: What kind of data is the organism.
    """

    label: Label = Label.RCSBENTITYHOSTORGANISM

    common_names: Set[str]
    parent_scientific_name: str
    scientific_name: str
    taxonomy_id: int
    provenance_source: str


class RcsbEntitySourceOrganism(NodeBase):
    """
    A node representing a source organism of a protein.

    Attributes:
        common_names: Common names from NCBI.
        parent_scientific_name: Parent's scientific name from NCBI.
        scientific_name: Scientific name from NCBI.
        taxonomy_id: Taxonomy ID from NCBI.
        provenance_source: What kind of data is the organism.
        source_type: Represents the type of the source organism.
    """

    label: Label = Label.RCSBENTITYSOURCEORGANISM

    common_names: Set[str]
    parent_scientific_name: str
    scientific_name: str
    taxonomy_id: int
    provenance_source: str
    source_type: str


class DrugNode(Entity):
    """
    A node representing a drug entity in the graph database.

    Attributes:
        drug_groups: Represents the drug groups that this entity belongs to.
        drugbank_id: Identity of the node in DrugBank.
        name: The compound official name.
        synonyms: Synonymous names for the drug.

    """

    label: Label = Label.DRUG

    drug_groups: Set[str]
    drugbank_id: str
    name: str
    synonyms: Set[str]


class DrugbankTarget(NodeBase):
    """
    Described the specific drug's target and where can find the target.

    Attributes:
        interaction_type: Represents interaction types.
        name: Reprsnts the target's name.
        ordinal: Distinguish different targets on the same drug.
        organism_common_name: Represents the target affect whom.
        seq_one_letter_code: Represents an amino acid sequence of the target.
    """

    label: Label = Label.DRUGBANKTARGET

    interaction_type: str
    name: str
    ordinal: int
    organism_common_name: str
    seq_one_letter_code: str


class Database(NodeBase):
    """
    A node representing which database can find the drug/protein's components.

    Attributes:
        reference_database_accession_code: Identity of the database where the protein or drug/target comes from.
        reference_database_name: Represents where the protein or drug's target comes from.
    """

    label: Label = Label.DATABASE

    reference_database_accession: str
    reference_database_name: str


class AnnotationNode(Entity):
    """
    A node representing an ontology annotation in the graph database.

    Attributes:
        description: The description of the annotation.

    """

    label: Label = Label.ANNOTATION

    description: str
