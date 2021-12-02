import { css, html, LitElement, PropertyValues } from "lit";
import "./graph-visualization";
import "./protein-selector";
import "./protein-details";
import { query, queryAll } from "lit/decorators.js";
import { GraphVisualization } from "./graph-visualization";
import { buildGraph } from "./graph_utils";
import { ANNOTATIONS, ENTRIES, PROTEINS } from "./example_data";
import { ProteinSelector } from "./protein-selector";

/**
 * Handles the display of search results.
 */
export class SearchResults extends LitElement {
  static tagName: string = "search-results";
  static styles = css`
    #selection {
      margin-right: 20px;
      /* Make sure this always takes priority for mouse events. */
      z-index: 1;
    }

    .fixed-column {
      height: 75vh;
    }

    #details {
      margin-left: 20px;
    }
  `;

  /**
   * Element displaying the graph visualization.
   * @private
   */
  @query("#graph-vis")
  private _graphVis!: GraphVisualization;

  /**
   * Gets all the protein selector cards.
   * @private
   */
  @queryAll("protein-selector")
  private _proteinSelectors!: ProteinSelector[];

  /**
   * @inheritDoc
   */
  protected render() {
    return html`
      <link rel="stylesheet" href="static/pdb-kg.css" />

      <!-- 3-column layout -->
      <div class="mc_row center">
        <!-- Protein selection -->
        <div class="column_width1 fixed-column" id="selection">
          <protein-selector></protein-selector>
        </div>

        <!-- Graph visualization -->
        <div class="column_width3 fixed-column" id="visualization">
          <div class="card">
            <span class="card-title">Related</span>
            <div class="card-content">
              <graph-visualization id="graph-vis"></graph-visualization>
            </div>
          </div>
        </div>

        <!-- Protein details -->
        <div class="column_width1 fixed-column" id="details">
          <protein-details></protein-details>
        </div>
      </div>
    `;
  }

  /**
   * @inheritDoc
   */
  protected firstUpdated(_: PropertyValues) {
    // Initialize the graph.
    this._graphVis.graph = buildGraph(PROTEINS, ANNOTATIONS, ENTRIES);

    // Add a listeners for the close button on the result cards.
    for (const resultCard of this._proteinSelectors) {
      resultCard.addEventListener(
        ProteinSelector.CLOSED_EVENT_NAME,
        (event: Event) => {
          (event.target as ProteinSelector).parentElement?.removeChild(
            event.target as HTMLElement
          );
        }
      );
    }
  }
}
