/**
 * @file Utilities for dealing with the underlying PDB graph data.
 */

import Graph from "graphology";
import {
  AnnotationResponse,
  EntryResponse,
  NodeLabel,
  ProteinResponse,
} from "typescript-axios";

/**
 * Common attributes for all node interfaces.
 */
interface Node {
  uuid?: string;
  label?: NodeLabel;

  // These attributes might or might not be present depending on the node type.
  id?: string;
  entryId?: string;
}

/**
 * Maps different node types to the colors that will be used for those nodes.
 */
const nodeColors: Map<NodeLabel, string> = new Map<NodeLabel, string>([
  [NodeLabel.PROTEIN, "#1EE649FF"],
  [NodeLabel.ANNOTATION, "#41E4E6FF"],
  [NodeLabel.ENTRY, "#024B2FFF"],
]);

/**
 * Adds nodes to the graph from an array.
 * @param {Graph} graph The graph to add nodes to. It will be modified in-place.
 * @param {Node[]} nodes The nodes to add.
 */
function addNodesToGraph(graph: Graph, nodes: Node[]) {
  const commonAttributes = { x: 0, y: 0, size: 10 };
  for (const node of nodes) {
    graph.addNode(node.uuid, {
      color: nodeColors.get(node.label as NodeLabel),
      label: node.id ?? node.entryId,
      ...commonAttributes,
    });
  }
}

/**
 * Builds a graph based on an interconnected set of nodes.
 * @param {ProteinResponse[]} proteins The protein nodes.
 * @param {AnnotationResponse[]} annotations The annotation nodes.
 * @param {EntryResponse} entries The entry nodes.
 * @return {Graph} The graph that it created.
 */
export function buildGraph(
  proteins: ProteinResponse[],
  annotations: AnnotationResponse[],
  entries: EntryResponse[]
): Graph {
  const graph = new Graph();

  // Add all the nodes to the graph.
  addNodesToGraph(graph, proteins);
  addNodesToGraph(graph, annotations);
  addNodesToGraph(graph, entries);

  // Add all the edges between proteins and annotations.
  for (const protein of proteins) {
    for (const annotation of protein.annotationUuids) {
      graph.addEdge(protein.uuid, annotation);
    }

    // Add all the edges between proteins and entries.
    graph.addEdge(protein.uuid, protein.entryUuid);
  }

  return graph;
}

/**
 * Adds the neighbors of an existing node to the graph.
 * @param {Graph} graph The graph to add nodes to.
 * @param {Node} rootNode The node that we're adding neighbors for.
 * @param {Node[]} neighbors The neighbors to add.
 */
export function addNeighbors(graph: Graph, rootNode: Node, neighbors: Node[]) {
  // Add the neighbors to the graph.
  addNodesToGraph(graph, neighbors);

  // Add the edges to the root node.
  for (const node of neighbors) {
    graph.addEdge(rootNode.uuid, node.uuid);
  }
}
