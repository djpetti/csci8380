/** Singleton API client used by the entire application. */
import {
  AnnotationResponse,
  Configuration,
  DefaultApi,
  EntryResponse,
  NodeBase,
  NodeLabel,
  ProteinResponse,
} from "typescript-axios";
import { LRUCache } from "typescript-lru-cache";

const api = new DefaultApi(
  new Configuration({ basePath: "http://localhost:8000" })
);

const cache = new LRUCache<string, any>();

/**
 * Used for translating raw node labels to enum values. Must be kept in-sync
 * with `NodeLabel` on the backend.
 */
const NODE_LABEL_TO_ENUM = new Map<string, NodeLabel>([
  [NodeLabel.NONE.toString(), NodeLabel.NONE],
  [NodeLabel.PROTEIN.toString(), NodeLabel.PROTEIN],
  [NodeLabel.DRUG.toString(), NodeLabel.DRUG],
  [NodeLabel.ENTRY.toString(), NodeLabel.ENTRY],
  [NodeLabel.ANNOTATION.toString(), NodeLabel.ANNOTATION],
  [NodeLabel.DRUGBANK_TARGET.toString(), NodeLabel.DRUGBANK_TARGET],
  [NodeLabel.DATABASE.toString(), NodeLabel.DATABASE],
  [NodeLabel.HOST_ORGANISM.toString(), NodeLabel.HOST_ORGANISM],
  [NodeLabel.SOURCE_ORGANISM.toString(), NodeLabel.SOURCE_ORGANISM],
]);

/**
 * Fixes the enums in raw nodes returned by the API.
 * @param {NodeBase} node The raw node to fix.
 * @return {NodeBase} The fixed node.
 */
function convertNode<NodeType extends NodeBase>(node: NodeType): NodeType {
  const converted = { ...node };

  // Fix the enums.
  converted.label = NODE_LABEL_TO_ENUM.get(converted.label as string);
  return converted;
}

/**
 * Checks if node info is in the cache and returns it if it is.
 * @param {string} nodeId: The ID of the node.
 * @return {any | undefined} The node info if present, otherwise null.
 */
function cacheParameters(nodeId: string): any | null {
  if (cache.has(nodeId)) {
    return cache.get(nodeId);
  }

  return null;
}

/**
 * Performs a natural-language query.
 * @param {string} queryText The text of the query.
 * @return {string[]} The UUIDs of the proteins found by the query.
 */
export async function getQuery(queryText: string): Promise<string[]> {
  const response = await api
    .queryQueryQueryTextGet(queryText)
    .catch(function (error) {
      console.error(error.toJSON());
      throw error;
    });

  return response.data;
}

/**
 * Gets the path between two nodes in the graph.
 * @param {string} startUuid The UUID of the starting node.
 * @param {string} endUuid The UUID of the ending node.
 * @param {number} maxLength The maximum-length path that we allow.
 * @return {NodeBase[]} The list of UUIDs of the nodes in the path, in
 *  order, or an empty list if there was no path within the length requirements.
 */
export async function getPath(
  startUuid: string,
  endUuid: string,
  maxLength?: number
): Promise<NodeBase[]> {
  const response = await api
    .getPathRequestGetPathGet(startUuid, endUuid, maxLength)
    .catch(function (error) {
      console.error(error.toJSON());
      throw error;
    });

  // Fix the enums.
  const path = [];
  for (const node of response.data) {
    path.push(convertNode(node));
  }

  return path;
}

/**
 * Gets all the neighbors of a particular node in the graph.
 * @param {string} nodeId The UUID of the root node.
 * @return {NodeBase[]} The list of UUIDs of the neighboring nodes.
 */
export async function getNeighbors(nodeId: string): Promise<NodeBase[]> {
  const response = await api
    .getNeighborsRequestGetNeighborsObjectIdGet(nodeId)
    .catch(function (error) {
      console.error(error.toJSON());
      throw error;
    });

  // Fix the enums.
  const path = [];
  for (const node of response.data) {
    path.push(convertNode(node));
  }

  return path;
}

/**
 * Gets detailed information about a protein.
 * @param {string} proteinId The UUID of the protein.
 * @return {ProteinResponse} The protein details.
 */
export async function getProtein(proteinId: string): Promise<ProteinResponse> {
  const cached = cacheParameters(proteinId);
  if (cached) {
    return cached;
  }

  const response = await api
    .getProteinRequestGetProteinProteinIdGet(proteinId)
    .catch(function (error) {
      console.error(error.toJSON());
      throw error;
    });

  const converted = convertNode(response.data);
  cache.set(proteinId, converted);
  return converted;
}

/**
 * Gets detailed information about an annotation.
 * @param {string} annotationId The UUID of the annotation.
 * @return {ProteinResponse} The annotation details.
 */
export async function getAnnotation(
  annotationId: string
): Promise<AnnotationResponse> {
  const cached = cacheParameters(annotationId);
  if (cached) {
    return cached;
  }

  const response = await api
    .getAnnotationRequestGetAnnotationAnnotationIdGet(annotationId)
    .catch(function (error) {
      console.error(error.toJSON());
      throw error;
    });

  const converted = convertNode(response.data);
  cache.set(annotationId, converted);
  return converted;
}

/**
 * Gets detailed information about an entry.
 * @param {string} entryId The UUID of the entry.
 * @return {ProteinResponse} The entry details.
 */
export async function getEntry(entryId: string): Promise<EntryResponse> {
  const cached = cacheParameters(entryId);
  if (cached) {
    return cached;
  }

  const response = await api
    .getEntryGetEntryEntryIdGet(entryId)
    .catch(function (error) {
      console.error(error.toJSON());
      throw error;
    });

  const converted = convertNode(response.data);
  cache.set(entryId, converted);
  return converted;
}
