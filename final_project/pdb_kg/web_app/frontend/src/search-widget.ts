import { css, html, LitElement } from "lit";
import { property, query } from "lit/decorators.js";
import "@material/mwc-textfield";
import "@material/mwc-button";
import "@material/mwc-linear-progress";
import "./search-results";
import { SearchResults } from "./search-results";
import { ProteinResponse } from "typescript-axios";
import { getProtein, getQuery } from "./api-client";

/**
 * Main element that handles searching and the display of results.
 */
export class SearchWidget extends LitElement {
  static tagName: string = "search-widget";
  static styles = css`
    .half-screen {
      min-width: 300px;
      max-width: 50%;
    }

    .full-width {
      width: 100%;
    }

    .hidden {
      display: none;
    }

    .overview_common {
      font-family: "Roboto", sans-serif;
      font-weight: 100;
      margin-top: 2rem;
      margin-left: auto;
      margin-right: auto;
      width: 50%;
      text-align: center;
      font-size: x-large;
    }

    .overview_conflicts {
      color: var(--theme-primary);
    }

    .overview_no_conflicts {
      color: var(--theme-gray);
    }

    #results {
      margin-top: 32px;
    }
  `;

  // Minimum length we allow for queries.
  private static MIN_QUERY_LENGTH: number = 4;

  /**
   * The query text that was entered by the user.
   */
  @property({ type: String })
  queryText: string = "";

  /** Whether a search is currently in-progress. */
  @property({ attribute: false })
  private _isSearching: boolean = false;

  /**
   * The element displaying search results.
   * @private
   */
  @query("#results")
  private _results!: SearchResults;

  /**
   * Checks whether the currently-entered names are valid.
   * @return {boolean} True if both names are valid.
   * @private
   */
  private isSearchValid(): boolean {
    return this.queryText.length >= SearchWidget.MIN_QUERY_LENGTH;
  }

  /**
   * Performs the search based on the user's input.
   * @param {string} query The query string entered by the user.
   * @return {ProteinResponse[]} The details for all the query results.
   * @private
   */
  private async makeSearchRequest(query: string): Promise<ProteinResponse[]> {
    // Perform the query.
    const queryResults = await getQuery(query);

    // Retrieve details for each result.
    const detailsPromises = queryResults.map((p) => getProtein(p));
    return Promise.all(detailsPromises);
  }

  /**
   * Callback performs the search and updates the data model accordingly.
   * @private
   */
  private search() {
    this._isSearching = true;

    // Perform the search.
    this.makeSearchRequest(this.queryText).then((response) => {
      this._isSearching = false;
      // Update the displayed results.
      // We have to copy the whole object instead of merely mutating it in order
      // to trigger the element update.
      this._results.searchResults = [
        { proteins: response },
        ...this._results.searchResults,
      ];
    });
  }

  /**
   * @inheritDoc
   */
  protected render() {
    // Class controlling the display of the search button.
    const searchDisplayClass = this._isSearching ? "hidden" : "";
    // Class controlling the display of the loading indicator.
    const loadingDisplayClass = this._isSearching ? "" : "hidden";

    return html`
      <link rel="stylesheet" href="static/pdb-kg.css" />

      <!-- Search box -->
      <div class="mc_row center">
        <div class="column_width1">
          <mwc-textfield
            label="Search for a protein or drug"
            id="search_bar"
            class="full-width"
            helper="Enter a PDB ID or some keywords."
            value="${this.queryText}"
            minLength="${SearchWidget.MIN_QUERY_LENGTH}"
            @change="${(event: InputEvent) =>
              (this.queryText = (event.target as HTMLInputElement).value)}"
          ></mwc-textfield>
        </div>
      </div>

      <div class="mc_row center">
        <div class="column_width1">
          <!-- Search button -->
          <mwc-button
            label="Search"
            icon="search"
            ?disabled="${!this.isSearchValid()}"
            class="${searchDisplayClass}"
            @click="${(_: Event) => this.search()}"
          >
          </mwc-button>

          <!-- Loading indicator -->
          <mwc-linear-progress
            indeterminate
            class="${loadingDisplayClass}"
          ></mwc-linear-progress>
        </div>

        <!-- Search result panels -->
        <div class="mc_row center">
          <div class="column_width1">
            <search-results id="results"></search-results>
          </div>
        </div>
      </div>
    `;
  }
}
