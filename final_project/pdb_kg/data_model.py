"""
Contains the data model used by this application.
"""


import enum
from typing import Any, Optional, Set, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


@enum.unique
class NodeLabel(enum.Enum):
    """
    Represents labels that nodes can have in the database.
    """

    NONE = "none"
    """
    Specifies that no specific label should be used.
    """
    PROTEIN = "protein"
    """
    Indicates that a node represents a protein.
    """
    DRUG = "drug"
    """
    Indicates that a node represents a drug.
    """
    ENTRY = "entry"
    """
    Indicates that a node represents a PDB entry.
    """
    ANNOTATION = "annotation"
    """
    Indicates that a node represents an ontology annotation.
    """
    DRUGBANK_TARGET = "drugbank_target"
    """
    Indicates that a node represents a drug's target.
    """
    DATABASE = "database"
    """
    Indicates that a node represents a protein database.
    """
    HOST_ORGANISM = "host_organism"
    """
    Indicates that a node represents a host organism of a protein.
    """
    SOURCE_ORGANISM = "source_organism"
    """
    Indicates that a node represents a source organism of a protein.
    """


def _snake_to_camel_case(snake: str) -> str:
    """
    Converts a field name in snake case, i.e. `my_field`, to one in camel
    case, i.e. `myField`.

    Args:
        snake: The field name in snake case.

    Returns:
        The field name in camel case.

    """
    words = snake.split("_")
    first_word = words[0]
    other_words = "".join((word.capitalize() for word in words[1:]))
    return f"{first_word}{other_words}"


class _ApiModelConfig:
    """
    Default config class for ApiModels.
    """

    alias_generator = _snake_to_camel_case
    allow_population_by_field_name = True
    allow_mutation = False


class ApiModel(BaseModel):
    """
    Implements the default configuration for models that are used as part of
    the API.
    """

    Config = _ApiModelConfig

    def json(self, *args: Any, by_alias: bool = True, **kwargs: Any) -> str:
        return super().json(*args, by_alias=by_alias, **kwargs)


class NodeBase(ApiModel):
    """
    Contains attributes shared by all models representing Neo4J nodes.

    Attributes:
        uuid: Unique identifier used by the graph DB to identify this node.
        label: The label of this node.

    """

    uuid: UUID = Field(default_factory=uuid4)
    label: NodeLabel = NodeLabel.NONE


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

    label: NodeLabel = NodeLabel.ENTRY

    entry_id: str
    protein_entity_ids: Set[str]

    publications: Tuple[Publication, ...]


class EntryResponse(EntryNode):
    """
    Response schema to be used for requests that require entry info as a
    response. It is very similar to `EntryNode`, but extends it with a few
    extra attributes.

    Attributes:
        protein_entity_uuids: The UUIDs of the corresponding entities in the
            database.

    """

    protein_entity_uuids: Set[UUID]


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
        entry_name: The name of the parent PDB entry for this protein.

        sequence: The sequence of the protein, in FASTA notation.

        annotations: Gene ontology annotations that are associated with this
            protein. They should be labeled by the GO ID.
        cofactors: Resource IDs of all associated cofactors for this protein.

    """

    label: NodeLabel = NodeLabel.PROTEIN

    entry_id: str
    # entry_name: str

    sequence: str

    annotations: Set[str]
    cofactors: Set[str]


class ProteinResponse(ProteinNode):
    """
    Response schema to be used for requests that require protein info as a
    response. It is very similar to `ProteinNode`, but extends it with a few
    extra attributes.

    Attributes:
        entry_uuid: The UUID in the database for the associated entry.
        annotation_uuids: The UUIDs in the database for the associated
            annotation nodes.
        cofactor_uuids: The UUIDs in the database for the associated cofactors.

    """

    entry_uuid: Optional[UUID]
    annotation_uuids: Set[UUID]
    cofactor_uuids: Set[UUID]


class HostOrganism(NodeBase):
    """
    A node representing a host organism of a protein.

    Attributes:
        common_names: Common names from NCBI.
        parent_scientific_name: Parent's scientific name from NCBI.
        scientific_name: Scientific name from NCBI.
        taxonomy_id: Taxonomy ID from NCBI.
        provenance_source: What kind of data is the organism.
    """

    label: NodeLabel = NodeLabel.HOST_ORGANISM

    common_names: Set[str]
    parent_scientific_name: str
    scientific_name: str
    taxonomy_id: int
    provenance_source: str


class SourceOrganism(NodeBase):
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

    label: NodeLabel = NodeLabel.SOURCE_ORGANISM

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
        drugbank_name: The compound official name.
        synonyms: Synonymous names for the drug.

    """

    label: NodeLabel = NodeLabel.DRUG

    drug_groups: Set[str]
    drugbank_id: str
    drugbank_name: str
    synonyms: Set[str]


class DrugbankTarget(NodeBase):
    """
    Described the specific drug's target and where can find the target.

    Attributes:
        interaction_type: Represents interaction types.
        name: Represents the target's name.
        ordinal: Distinguish different targets on the same drug.
    """

    label: NodeLabel = NodeLabel.DRUGBANK_TARGET

    interaction_type: str
    name: str
    ordinal: int


class AnnotationNode(Entity):
    """
    A node representing an ontology annotation in the graph database.

    Attributes:
        description: The description of the annotation.

    """

    label: NodeLabel = NodeLabel.ANNOTATION

    description: str


class AnnotationResponse(AnnotationNode):
    """
    Response schema to be used for requests that require annotation info as a
    response.
    """


class Database(NodeBase):
    """
    A node representing which database can find the drug/protein's components.

    Attributes:
        reference_database_accession: Identity of the database where the
            protein or drug/target comes from.
        reference_database_name: Represents where the protein or drug's target
            comes from.
    """

    label: NodeLabel = NodeLabel.DATABASE

    reference_database_accession: str
    reference_database_name: str
