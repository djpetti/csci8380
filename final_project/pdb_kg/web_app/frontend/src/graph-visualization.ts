import { html, LitElement, PropertyValues, css } from "lit";
import { query } from "lit/decorators.js";
import Graph from "graphology";
import Sigma from "sigma";
import random from "graphology-layout/random";

/**
 * Element for visualizing the relationship graph among proteins.
 */
export class GraphVisualization extends LitElement {
  static tagName: string = "graph-visualization";
  static styles = css`
    #graph {
      width: 100%;
      height: 30vh;
      /* This is a hack to get Sigma to display without an offset.
         I assume Sigma isn't playing nice with LitElement or something. */
      margin-left: -50%;
      padding: 0;
      overflow: hidden;
    }
  `;

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
   * @inheritDoc
   */
  protected render() {
    return html` <div id="graph"></div> `;
  }

  /**
   * @inheritDoc
   */
  protected firstUpdated(_: PropertyValues) {
    // Draw the graph.
    const graph = new Graph();

    graph.addNode("John", { x: 0, y: 0, size: 5, label: "John" });
    graph.addNode("Mary", { x: 0, y: 0, size: 3, label: "Mary" });

    graph.addEdge("John", "Mary");

    random.assign(graph);

    this._renderer = new Sigma(graph, this._graphContainer);
  }
}
