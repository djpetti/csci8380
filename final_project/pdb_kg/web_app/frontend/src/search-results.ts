import { css, html, LitElement, PropertyValues } from "lit";
import "./graph-visualization";
import "./protein-selector";
import "./protein-details";
import { property, query } from "lit/decorators.js";
import { GraphVisualization } from "./graph-visualization";
import { buildGraph, createNeighborhoodGraph } from "./graph-utils";
import { ANNOTATIONS, ENTRIES, PROTEINS } from "./example_data";
import { ProteinSelector } from "./protein-selector";
import { ProteinResponse } from "typescript-axios";
import { ProteinDetails } from "./protein-details";

/**
 * Represents the result of a search.
 */
export interface SearchData {
  // The proteins that the search found.
  proteins: ProteinResponse[];
}

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
   * Contains the search results that we want to display.
   */
  @property({ attribute: false })
  searchResults: SearchData[] = [];

  /**
   * Element displaying the graph visualization.
   * @private
   */
  @query("#graph-vis")
  private _graphVis!: GraphVisualization;

  /**
   * The container displaying protein selections.
   * @private
   */
  @query("#selection")
  private _selectionContainer!: HTMLElement;

  /**
   * The container displaying protein details.
   * @private
   */
  @query("#details")
  private _detailsContainer!: HTMLElement;

  /**
   * Maps search results to the corresponding element displaying them.
   * @private
   */
  private _searchResultToElement = new Map<SearchData, ProteinSelector>();

  /**
   * Maps selected protein UUIDs to corresponding details cards.
   */
  private _selectedProteinsToElement = new Map<string, ProteinDetails>();

  /**
   * @inheritDoc
   */
  protected render() {
    return html`
      <link rel="stylesheet" href="static/pdb-kg.css" />

      <!-- 3-column layout -->
      <div class="mc_row center">
        <!-- Protein selection -->
        <div class="column_width1 fixed-column" id="selection"></div>

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
        <div class="column_width1 fixed-column" id="details"></div>
      </div>
    `;
  }

  /**
   * Gets all the proteins that are currently selected in all search results.
   * @return {ProteinResponse[]} The set of all unique selected proteins.
   * @private
   */
  private getAllSelectedProteins(): ProteinResponse[] {
    const selectedProteins: ProteinResponse[] = [];
    // Keep track of UUIDs so we don't add duplicates.
    const seenUuids = new Set<string>();

    for (const resultCard of this._selectionContainer.querySelectorAll(
      "protein-selector"
    )) {
      const uniqueProteins = (
        resultCard as ProteinSelector
      ).selectedProteins.filter((p) => !seenUuids.has(p.uuid as string));
      selectedProteins.push(...uniqueProteins);
    }

    return selectedProteins;
  }

  /**
   * Updates the graph visualization to contain the selected nodes.
   * @param {ProteinResponse[]} selectedProteins The currently-selected proteins.
   * @private
   */
  private updateGraphVisualization(selectedProteins: ProteinResponse[]) {
    createNeighborhoodGraph(selectedProteins).then(
      (graph) => (this._graphVis.graph = graph)
    );
  }

  /**
   * Updates the selected proteins in the UI based on the user's selections.
   * @param {ProteinResponse[]} selectedProteins The proteins that the user selected.
   * @private
   */
  private updateSelectedProteins(selectedProteins: ProteinResponse[]) {
    // Update the graph visualization.
    this.updateGraphVisualization(selectedProteins);

    // Add protein details.
    for (const protein of selectedProteins) {
      if (this._selectedProteinsToElement.has(protein.uuid as string)) {
        // Protein was selected before. We should not need to change anything.
        continue;
      }

      // Otherwise, add the details card.
      const detailsCard = new ProteinDetails();
      detailsCard.protein = protein;
      // Add it to the DOM.
      this._detailsContainer.appendChild(detailsCard);

      this._selectedProteinsToElement.set(protein.uuid as string, detailsCard);
    }

    // Prepare a set of selected protein UUIDs.
    const selectedUuids = new Set<string>(
      selectedProteins.map((p) => p.uuid as string)
    );
    // Remove protein details.
    for (const [proteinUuid, card] of this._selectedProteinsToElement) {
      if (selectedUuids.has(proteinUuid)) {
        // Protein was not selected before. We should not need to change anything.
        continue;
      }

      // Otherwise, remove the details card.
      this._detailsContainer.removeChild(card);

      this._selectedProteinsToElement.delete(proteinUuid);
    }
  }

  /**
   * Updates the search result cards shown on the left.
   * @private
   */
  private updateSearchResults() {
    // Add any missing results.
    for (const result of this.searchResults) {
      if (this._searchResultToElement.has(result)) {
        // We are already displaying these results. No need to change anything.
        continue;
      }

      // Create a new element to display the search results.
      const selector = new ProteinSelector();
      selector.proteins = result.proteins;

      // Add it to the DOM.
      this._selectionContainer.appendChild(selector);
      this._searchResultToElement.set(result, selector);

      // Add a listener for the close button.
      selector.addEventListener(
        ProteinSelector.CLOSED_EVENT_NAME,
        (_: Event) =>
          (this.searchResults = this.searchResults.filter((e) => e != result))
      );
      // Add a listener for selection changes.
      selector.addEventListener(
        ProteinSelector.SELECTION_CHANGED_EVENT_NAME,
        (_: Event) => this.updateSelectedProteins(this.getAllSelectedProteins())
      );
    }

    // Remove any closed results.
    for (const result of this._searchResultToElement.keys()) {
      if (this.searchResults.includes(result)) {
        // We haven't closed this yet. No need to change anything.
        continue;
      }

      // Remove the element.
      const selector = this._searchResultToElement.get(
        result
      ) as ProteinSelector;
      this._selectionContainer.removeChild(selector);

      this._searchResultToElement.delete(result);
    }

    // It's possible we removed a card with selected proteins, so we need to
    // update the selections again.
    this.updateSelectedProteins(this.getAllSelectedProteins());
  }

  /**
   * @inheritDoc
   */
  protected updated(changedProperties: PropertyValues) {
    if (changedProperties.has("searchResults")) {
      this.updateSearchResults();
    }
  }

  /**
   * @inheritDoc
   */
  protected firstUpdated(_: PropertyValues) {
    // Initialize the graph.
    this._graphVis.graph = buildGraph(PROTEINS, ANNOTATIONS, ENTRIES);
  }
}
