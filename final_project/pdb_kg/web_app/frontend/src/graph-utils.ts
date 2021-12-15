/**
 * @file Utilities for dealing with the underlying PDB graph data.
 */

import Graph from "graphology";
import {
  AnnotationResponse,
  EntryResponse,
  NodeBase,
  NodeLabel,
  ProteinResponse,
} from "typescript-axios";
import {
  getAnnotation,
  getEntry,
  getNeighbors,
  getPath,
  getProtein,
} from "./api-client";

/**
 * Common attributes for all node interfaces.
 */
interface Node extends NodeBase {
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
  [NodeLabel.DRUG, "#23FBA8FF"],
]);

/**
 * Adds nodes to the graph from an array.
 * @param {Graph} graph The graph to add nodes to. It will be modified in-place.
 * @param {Node[]} nodes The nodes to add.
 */
function addNodesToGraph(graph: Graph, nodes: Node[]) {
  const commonAttributes = { x: 0, y: 0, size: 10 };
  for (const node of nodes) {
    if (graph.hasNode(node.uuid)) {
      // We already have this node.
      continue;
    }

    // Determine the label based on what attributes we have.
    let label: string = "";
    if (node.entryId && node.id) {
      label = `${node.entryId}/${node.id}`;
    } else if (node.entryId) {
      label = node.entryId;
    } else {
      label = node.id as string;
    }

    graph.addNode(node.uuid, {
      color: nodeColors.get(node.label as NodeLabel),
      label: label,
      ...commonAttributes,
    });
  }
}

/**
 * Retrieves detailed information about a node from the backend.
 * @param {NodeBase} node The node to get details for.
 * @return {Node} The node details.
 */
async function getNodeDetails(node: NodeBase): Promise<Node> {
  switch (node.label) {
    case NodeLabel.PROTEIN: {
      return await getProtein(node.uuid as string);
    }
    case NodeLabel.ENTRY: {
      return await getEntry(node.uuid as string);
    }
    case NodeLabel.ANNOTATION: {
      return await getAnnotation(node.uuid as string);
    }
    default: {
      // In this case, there are is no more info we can get.
      return node;
    }
  }
}

/**
 * Same as `getNodeDetails`, but retrieves details for an entire set of nodes.
 * @param {Set<NodeBase>} nodes The nodes to get details for.
 * @return {Set<Node>} The details of the nodes.
 */
async function getAllNodeDetails(
  nodes: Iterable<NodeBase>
): Promise<Set<Node>> {
  const responses = new Set<Node>();
  for (const node of nodes) {
    responses.add(await getNodeDetails(node));
  }

  return responses;
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

/**
 * Creates a graph containing several nodes as well as all the nodes that connect
 * them. It will make the necessary backend requests in order to find these nodes.
 * @param {NodeBase[]} nodes The nodes that we want in the graph.
 * @return {Graph} The graph containing the nodes and all connections.
 */
export async function createNeighborhoodGraph(
  nodes: NodeBase[]
): Promise<Graph> {
  // If we have more than one node, we will have to find a path connecting them.
  const backboneNodes: NodeBase[] = [];
  let connectedBackbone: boolean = true;
  for (let i = 0; i < nodes.length - 1; ++i) {
    const pathStart = nodes[i];
    const pathEnd = nodes[i + 1];
    const path = await getPath(
      pathStart.uuid as string,
      pathEnd.uuid as string
    );

    if (path.length == 0) {
      // The path might be empty if it's too long, and that's okay. In that case,
      // we just show disjoint graphs.
      connectedBackbone = false;
      backboneNodes.push(pathStart, pathEnd);
    } else {
      backboneNodes.push(...path);
    }
  }
  if (nodes.length == 1) {
    // There is an edge-case when we only have a single node in the path.
    backboneNodes.push(...nodes);
  }

  const backboneNodeDetails = await getAllNodeDetails(backboneNodes);

  const graph = new Graph();
  addNodesToGraph(graph, [...backboneNodeDetails]);
  if (connectedBackbone) {
    // Add edges between all the backbone nodes.
    for (let i = 0; i < backboneNodes.length - 1; ++i) {
      graph.addEdge(backboneNodes[i].uuid, backboneNodes[i + 1].uuid);
    }
  }

  // Flesh out the graph with the neighbors of each node.
  for (const node of backboneNodeDetails) {
    const neighbors = await getNeighbors(node.uuid as string);
    const neighborDetails = await getAllNodeDetails(neighbors);

    addNodesToGraph(graph, [...neighborDetails]);
    // Add edges from the root to each neighbor.
    for (const neighbor of neighbors) {
      if (!graph.hasEdge(node.uuid, neighbor.uuid)) {
        graph.addEdge(node.uuid, neighbor.uuid);
      }
    }
  }

  return graph;
}
