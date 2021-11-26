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

    DrugbankContainerIdentifiers = enum.auto()
    DrugbankInfo = enum.auto()
    DrugbankTarget = enum.auto()


class NodeBase(BaseModel):
    """
    Contains attributes shared by all models representing Neo4J nodes.

    Attributes:
        uuid: Unique identifier used by the graph DB to identify this node.
        label: The label of this node.

    """

    uuid: UUID = Field(default_factory=uuid4)
    label: Label


class DrugbankContainerIdentifiers(NodeBase):
    """"""

    label: Label = Label.DrugbankContainerIdentifiers

    drugbank_id: str


class DrugbankInfo(NodeBase):
    """"""

    label: Label = Label.DrugbankInfo

    drug_groups: Set[str]
    drugbank_id: str
    name: str
    synonyms: Set[str]


class DrugbankTarget(NodeBase):
    """"""

    label: Label = Label.DrugbankTarget

    interaction_type: str
    name: str
    ordinal: int
    organism_common_name: str
    reference_database_accession_code: str
    reference_database_name: str
    seq_one_letter_code: str
