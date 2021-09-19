import {
  css,
  html,
  LitElement,
  property,
  TemplateResult,
  query,
  PropertyValues,
} from "lit-element";
import "@material/mwc-textfield";
import "@material/mwc-button";
import "@material/mwc-linear-progress";
import { checkNames } from "./api-client";
import {
  ConflictCheckResult,
  ConflictCheckResultLevelEnum,
} from "typescript-axios";
import { PaperTable } from "./paper-table";

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
  `;

  // Minimum length we allow for names.
  private static MIN_NAME_LENGTH: number = 3;

  /**
   * The name of the first researcher to check.
   */
  @property({ type: String })
  firstName: string = "";

  /**
   * The name of the second researcher to check.
   */
  @property({ type: String })
  secondName: string = "";

  /**
   * Keeps track of the search results.
   */
  @property({ attribute: false })
  private searchResults?: ConflictCheckResult;

  /** Whether a search is currently in-progress. */
  @property({ attribute: false })
  private isSearching: boolean = false;

  /** Table of common papers. */
  @query("#paper_table")
  private paperTable?: PaperTable;

  /**
   * Runs a conflict-of-interest search on the two current names and updates
   * the display with the result.
   * @private
   */
  private search() {
    this.isSearching = true;

    checkNames(this.firstName, this.secondName).then((result) => {
      this.searchResults = result;
      this.isSearching = false;
    });
  }

  /**
   * Checks whether the currently-entered names are valid.
   * @return {boolean} True if both names are valid.
   * @private
   */
  private isSearchValid(): boolean {
    return (
      this.firstName.length >= SearchWidget.MIN_NAME_LENGTH &&
      this.secondName.length >= SearchWidget.MIN_NAME_LENGTH
    );
  }

  /**
   * Gets the proper overview text for a specified conflict level.
   * @return {TemplateResult} The overview text to use, or undefined if there are no search results.
   * @private
   */
  private getOverviewText(): TemplateResult | undefined {
    switch (this.searchResults?.level) {
      case ConflictCheckResultLevelEnum.NONE: {
        return html`<h1 class="overview_common overview_no_conflicts">
          No Conflicts Found
        </h1>`;
      }
      case ConflictCheckResultLevelEnum.LOW: {
        return html`<h1 class="overview_common overview_conflicts">
          Mild Conflicts Found
        </h1>`;
      }
      case ConflictCheckResultLevelEnum.MEDIUM: {
        return html`<h1 class="overview_common overview_conflicts">
          Moderate Conflicts Found
        </h1>`;
      }
      case ConflictCheckResultLevelEnum.STRONG: {
        return html`<h1 class="overview_common overview_conflicts">
          Severe Conflicts Found
        </h1>`;
      }
    }
  }

  /**
   * @inheritDoc
   */
  protected render() {
    // Class controlling the display of the results.
    const resultDisplayClass = this.searchResults !== undefined ? "" : "hidden";
    // Class controlling the display of the search button.
    const searchDisplayClass = this.isSearching ? "hidden" : "";
    // Class controlling the display of the loading indicator.
    const loadingDisplayClass = this.isSearching ? "" : "hidden";

    return html`
      <link rel="stylesheet" href="static/project1.css" />

      <!-- Search boxes -->
      <div class="row center">
        <div class="column_width1 half-screen">
          <mwc-textfield
            label="Researcher #1 Name"
            id="first_name"
            class="full-width"
            helper="The name of the first researcher"
            value="${this.firstName}"
            minLength="${SearchWidget.MIN_NAME_LENGTH}"
            @change="${(event: InputEvent) =>
              (this.firstName = (event.target as HTMLInputElement).value)}"
          ></mwc-textfield>
        </div>
        <div class="column_width1 half-screen">
          <mwc-textfield
            label="Researcher #2 Name"
            id="second_name"
            class="full-width"
            helper="The name of the second researcher"
            value="${this.secondName}"
            minLength="${SearchWidget.MIN_NAME_LENGTH}"
            @change="${(event: InputEvent) =>
              (this.secondName = (event.target as HTMLInputElement).value)}"
          ></mwc-textfield>
        </div>
      </div>

      <div class="row center">
        <div class="column_width1">
          <!-- Search button -->
          <mwc-button
            label="Search"
            icon="search"
            @click="${this.search}"
            ?disabled="${!this.isSearchValid()}"
            class="${searchDisplayClass}"
          >
          </mwc-button>

          <!-- Loading indicator -->
          <mwc-linear-progress
            indeterminate
            class="${loadingDisplayClass}"
          ></mwc-linear-progress>
        </div>
      </div>

      <!-- Result overview -->
      <div class="row center ${resultDisplayClass}">
        <div class="column_width1">${this.getOverviewText()}</div>
      </div>

      <!-- Result table -->
      <div class="row center ${resultDisplayClass}">
        <div class="column_width1">
          <paper-table id="paper_table"></paper-table>
        </div>
      </div>
    `;
  }

  /**
   * @inheritDoc
   */
  protected updated(_changedProperties: PropertyValues) {
    if (
      _changedProperties.has("searchResults") &&
      this.paperTable !== undefined
    ) {
      // Update the table of papers.
      this.paperTable.searchResults = this.searchResults;
    }
  }
}
