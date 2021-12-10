import { html, css, LitElement, TemplateResult } from "lit";
import { property } from "lit/decorators.js";
import "@material/mwc-list";
import "@material/mwc-list/mwc-list-item";
import { ProteinResponse } from "typescript-axios";
import "@material/mwc-icon-button";
import { SelectedEvent } from "@material/mwc-list";

/**
 * Interface for a custom event indicating that the selection has changed.
 */
export interface SelectionChangedEvent extends Event {
  // The detail attribute is now the structures for the proteins
  // that are currently selected.
  detail: ProteinResponse[];
}

/**
 * Provides a simple selection mechanism for search results.
 */
export class ProteinSelector extends LitElement {
  static tagName: string = "protein-selector";
  static styles = css`
    #close-button {
      float: right;
      margin: 10px;
    }
  `;

  /**
   * Name for the custom event signaling that the user has clicked the close
   * button.
   */
  static CLOSED_EVENT_NAME: string = "selector-closed";

  /**
   * Name for the custom event signaling that the user has changed their selection.
   */
  static SELECTION_CHANGED_EVENT_NAME: string = "selector-selection-changed";

  /**
   * Info for the proteins that will be displayed by this element.
   */
  @property({ attribute: false })
  proteins: ProteinResponse[] = [];

  /**
   * Keeps track of the indices of selected entries.
   */
  private _selectedIndices: Set<number> = new Set<number>();

  /**
   * Gets the info for the proteins that are currently selected.
   * @return {ProteinResponse[]} The currently-selected proteins.
   */
  get selectedProteins(): ProteinResponse[] {
    const selectedProteins = [];
    for (const index of this._selectedIndices) {
      selectedProteins.push(this.proteins[index]);
    }

    return selectedProteins;
  }

  /**
   * Renders the list item for a single protein.
   * @param {ProteinResponse} protein The protein information to render.
   * @return {TemplateResult} The rendered HTMl.
   * @private
   */
  private static renderProtein(protein: ProteinResponse): TemplateResult {
    return html`
      <mwc-list-item twoline>
        <span>${protein.entryId}/${protein.id}</span>
        <span slot="secondary">${protein.name}</span>
      </mwc-list-item>
    `;
  }

  /**
   * Handler for the event that is triggered when the user changes their selection.
   * @param {SelectedEvent} event The event that was triggered.
   * @private
   */
  private handleSelection(event: SelectedEvent) {
    // Update the selected indices.
    this._selectedIndices = event.detail.index as Set<number>;

    // Dispatch a new event with this information.
    this.dispatchEvent(
      new CustomEvent<ProteinResponse[]>(
        ProteinSelector.SELECTION_CHANGED_EVENT_NAME,
        { bubbles: true, composed: true, detail: this.selectedProteins }
      )
    );
  }

  /**
   * @inheritDoc
   */
  protected render() {
    return html`
      <link rel="stylesheet" href="static/pdb-kg.css" />

      <div class="card">
        <mwc-icon-button
          icon="close"
          id="close-button"
          @click="${(_: Event) =>
            // Dispatch the custom close event when we click the close button.
            this.dispatchEvent(
              new CustomEvent(ProteinSelector.CLOSED_EVENT_NAME, {
                bubbles: true,
                composed: true,
              })
            )}"
        ></mwc-icon-button>
        <div class="card-content">
          <mwc-list activatable multi @selected="${this.handleSelection}">
            ${this.proteins.map((protein) =>
              ProteinSelector.renderProtein(protein)
            )}
          </mwc-list>
        </div>
      </div>
    `;
  }
}
