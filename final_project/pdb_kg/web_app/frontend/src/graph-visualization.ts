import {html, LitElement, query} from "lit-element";
import {DataSet, Network} from "vis-network";

/**
 * Element for visualizing the relationship graph among proteins.
 */
export class GraphVisualization extends LitElement {
  static tagName: string = "graph-visualization";


  /**
   * The actual element that will store the graph.
   */
  @query("#graph")
  _graph!: HTMLElement;

  /**
   * @inheritDoc
   */
  protected render() {
    return html`
        <div id="graph"></div>
    `
  }
}
