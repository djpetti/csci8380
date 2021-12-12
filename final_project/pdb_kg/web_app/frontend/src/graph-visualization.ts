import { html, LitElement, PropertyValues, css } from "lit";
import { property, query } from "lit/decorators.js";
import Graph from "graphology";
import Sigma from "sigma";
import ForceSupervisor from "graphology-layout-force/worker";
import random from "graphology-layout/random";

/**
 * Element for visualizing the relationship graph among proteins.
 */
export class GraphVisualization extends LitElement {
  static tagName: string = "graph-visualization";
  static styles = css`
    #graph {
      width: 100%;
      height: 50vh;
      /* This is a hack to get Sigma to display without an offset.
         I assume Sigma isn't playing nice with LitElement or something. */
      margin-left: -50%;
      padding: 0;
      overflow: hidden;
    }
  `;

  /**
   * The graph that we want to display.
   */
  @property({ attribute: false })
  graph!: Graph;

  /**
   * The container element that will store the graph.
   */
  @query("#graph")
  private _graphContainer!: HTMLElement;

  /**
   * The renderer for the graph.
   */
  private _renderer!: Sigma;

  /**
   * Manages the graph layout automatically.
   * @private
   */
  private _layout!: ForceSupervisor;

  /**
   * @inheritDoc
   */
  protected render() {
    return html` <div id="graph"></div> `;
  }

  /**
   * Draws the graph initially, setting up the renderer and all the interaction callbacks.
   * This should only have to be called after the graph is first updated.
   * @private
   */
  private initGraph() {
    // Draw the graph.
    this._renderer = new Sigma(this.graph, this._graphContainer);

    // Initialize the node positions randomly.
    random.assign(this.graph);
    // Use the force layout for the graph.
    this._layout = new ForceSupervisor(this.graph);
    this._layout.start();
  }

  /**
   * Updates an existing graph to match a new one.
   * @private
   */
  private updateGraph() {
    // Draw the new graph.
    // Update the nodes.
    this._renderer.getGraph().forEachNode(nodeId => {
      if (!this.graph.hasNode(nodeId)) {
        // This node has been removed.
        this._renderer.getGraph().dropNode(nodeId);
      }
    });
    this.graph.forEachNode((nodeId, attributes) => {
      if (!this._renderer.getGraph().hasNode(nodeId)) {
        // This node has been added.
        this._renderer.getGraph().addNode(nodeId, attributes);
      }
    });

    // Update the edges.
    this._renderer.getGraph().forEachEdge((edgeId) => {
      if (!this.graph.hasEdge(edgeId)) {
        // This edge has been removed.
        this._renderer.getGraph().dropEdge(edgeId);
      }
    });
    this.graph.forEachEdge((edgeId, attributes, source, target) => {
      if (!this._renderer.getGraph().hasEdge(edgeId)) {
        // This edge has been added.
        this._renderer.getGraph().addEdge(source, target, attributes);
      }
    });

    // Force a layout update.
    random.assign(this._renderer.getGraph());
  }

  /**
   * @inheritDoc
   */
  protected firstUpdated(changedProperties: PropertyValues) {
    if (changedProperties.has("graph")) {
      // Draw the new graph.
      this.initGraph();
    }
  }

  /**
   * @inheritDoc
   */
  protected updated(changedProperties: PropertyValues) {
    if (changedProperties.has("graph")) {
      this.updateGraph();
    }
  }
}
