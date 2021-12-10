import {
  AnnotationResponse,
  EntryResponse,
  NodeLabel,
  ProteinResponse,
} from "typescript-axios";

export const PROTEINS: ProteinResponse[] = [
  {
    label: NodeLabel.PROTEIN,
    uuid: "protein1",
    id: "4HHB",
    name: "Hemoglobin subunit alpha",
    entryId: "2423",
    sequence: "FASTA",
    annotations: new Set(["GO:12345"]),
    cofactors: new Set(),
    entryUuid: "entry1",
    cofactorUuids: new Set(),
    annotationUuids: new Set(["asfs123asa21"]),
  },
  {
    label: NodeLabel.PROTEIN,
    uuid: "protein2",
    id: "4HHC",
    name: "Hemoglobin subunit beta",
    entryId: "2423",
    sequence: "FASTA",
    annotations: new Set(["GO:12345"]),
    cofactors: new Set(),
    entryUuid: "entry1",
    cofactorUuids: new Set(),
    annotationUuids: new Set(["asfs123asa21"]),
  },
];

export const ENTRIES: EntryResponse[] = [
  {
    label: NodeLabel.ENTRY,
    uuid: "entry1",
    entryId: "2423",
    proteinEntityIds: new Set(),
    publications: [
      {
        title: "Thoughts about Things: A Survey",
        authors: ["Daniel Petti", "Zach Ross"],
        year: 2020,
      },
      {
        title: "More Thoughts about Things",
        authors: ["Daniel Petti", "Zach Ross"],
        year: 2021,
      },
    ],
    proteinEntityUuids: new Set(["asdf1", "asdf2"]),
  },
];

export const ANNOTATIONS: AnnotationResponse[] = [
  {
    label: NodeLabel.ANNOTATION,
    uuid: "asfs123asa21",
    id: "GO:1905690",
    name: "Bio Stuff",
    description: "Mumble mumble mitochondria mumble",
  },
];
