"""
Contains the data model used by this application.
"""


import enum
from typing import Set

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


class DrugCommon(Entity):
    """
    Common fields for all representations of a drug.

    Attributes:
        drug_groups: Represents the drug groups that this entity belongs to.

    """

    drug_groups: Set[str]


class DrugNode(DrugCommon, NodeMixin):
    """
    A node representing a drug in the graph database.
    """

    LABEL = Label.DRUG
