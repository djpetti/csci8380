import { html, LitElement, TemplateResult } from "lit";
import { property } from "lit/decorators.js";
import "@material/mwc-list";
import "@material/mwc-list/mwc-list-item";
import { ProteinResponse } from "typescript-axios";

/**
 * Provides a simple selection mechanism for search results.
 */
export class ProteinSelector extends LitElement {
  static tagName: string = "protein-selector";

  /**
   * Info for the proteins that will be displayed by this element.
   */
  @property({ attribute: false })
  proteins: ProteinResponse[] = [
    {
      id: "4HHB",
      name: "Hemoglobin subunit alpha",
      entryId: "entry",
      sequence: "FASTA",
      annotations: new Set(),
      cofactors: new Set(),
      entryUuid: "",
      cofactorUuids: new Set(),
      annotationUuids: new Set(),
    },
    {
      id: "4HHC",
      name: "Hemoglobin subunit beta",
      entryId: "entry",
      sequence: "FASTA",
      annotations: new Set(),
      cofactors: new Set(),
      entryUuid: "",
      cofactorUuids: new Set(),
      annotationUuids: new Set(),
    },
  ];

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
      <mwc-list activatable>
        ${this.proteins.map((protein) =>
          ProteinSelector.renderProtein(protein)
        )}
      </mwc-list>
    `;
  }
}
