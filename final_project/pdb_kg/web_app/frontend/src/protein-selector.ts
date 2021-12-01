import { html, css, LitElement, TemplateResult } from "lit";
import { property } from "lit/decorators.js";
import "@material/mwc-list";
import "@material/mwc-list/mwc-list-item";
import { ProteinResponse } from "typescript-axios";
import "@material/mwc-icon-button";
import { PROTEINS } from "./example_data";

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
   * Info for the proteins that will be displayed by this element.
   */
  @property({ attribute: false })
  proteins: ProteinResponse[] = PROTEINS;

  /**
   * Renders the list item for a single protein.
   * @param {ProteinResponse} protein The protein information to render.
   * @return {TemplateResult} The rendered HTMl.
   * @private
   */
  private static renderProtein(protein: ProteinResponse): TemplateResult {
    return html`
      <mwc-list-item twoline>
        <span>${protein.id}</span>
        <span slot="secondary">${protein.name}</span>
      </mwc-list-item>
    `;
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
          <mwc-list activatable>
            ${this.proteins.map((protein) =>
              ProteinSelector.renderProtein(protein)
            )}
          </mwc-list>
        </div>
      </div>
    `;
  }
}
