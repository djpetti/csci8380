import { html, LitElement } from "lit";
import "@material/mwc-list";
import "@material/mwc-list/mwc-list-item";

/**
 * Provides a simple selection mechanism for search results.
 */
export class ProteinSelector extends LitElement {
  static tagName: string = "protein-selector";

  /**
   * @inheritDoc
   */
  protected render() {
    return html`
      <mwc-list activatable>
        <mwc-list-item twoline>
          <span>Protein 1</span>
          <span slot="secondary">This is a protein.</span>
        </mwc-list-item>
        <mwc-list-item selected activated twoline>
          <span>Protein 2</span>
          <span slot="secondary">This is another protein.</span>
        </mwc-list-item>
        <mwc-list-item twoline>
          <span>Protein 3</span>
          <span slot="secondary">This is yet another protein.</span>
        </mwc-list-item>
      </mwc-list>
    `;
  }
}
