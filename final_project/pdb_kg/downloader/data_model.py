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

        sequence: The sequence of the protein, in FASTA notation.

        annotations: Gene ontology annotations that are associated with this
            protein. They should be labeled by the GO ID.
        cofactors: Resource IDs of all associated cofactors for this protein.

    """

    label: Label = Label.PROTEIN

    entry_id: str

    sequence: str

    annotations: Set[str]
    cofactors: Set[str]


class DrugNode(Entity):
    """
    A node representing a drug entity in the graph database.

    Attributes:
        drug_groups: Represents the drug groups that this entity belongs to.
        synonyms: Synonymous names for the drug.

    """

    label: Label = Label.DRUG

    drug_groups: Set[str]
    synonyms: Set[str]


class AnnotationNode(Entity):
    """
    A node representing an ontology annotation in the graph database.

    Attributes:
        description: The description of the annotation.

    """

    label: Label = Label.ANNOTATION

    description: str
