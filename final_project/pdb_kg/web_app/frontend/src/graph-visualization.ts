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
   * Draws the graph, setting up the renderer and all the interaction callbacks.
   * This should only have to be called after the graph is updated.
   * @private
   */
  private drawGraph() {
    // Draw the graph.
    this._renderer = new Sigma(this.graph, this._graphContainer);

    // Initialize the node positions randomly.
    random.assign(this.graph);
    // Use the force layout for the graph.
    this._layout = new ForceSupervisor(this.graph);
    this._layout.start();
  }

  /**
   * @inheritDoc
   */
  protected updated(changedProperties: PropertyValues) {
    if (changedProperties.has("graph")) {
      // Draw the new graph.
      this.drawGraph();
    }
  }
}
